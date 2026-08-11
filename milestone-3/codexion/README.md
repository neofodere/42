*This project has been created as part of the curriculum of 42 by nfodere-.*

# codexion

## Description

**codexion** simulates a group of coders sitting around a circular co-working
hub, all competing for a scarce shared resource: **USB dongles**. It is a
concurrency exercise built on top of the classic "dining philosophers"
problem, with three extra layers on top of the textbook version:

- a **cooldown** period during which a released dongle cannot be re-taken,
- a choice of **arbitration policy** (`fifo` or `edf`) used to decide who
  gets a contested dongle,
- a **priority queue implemented as a binary heap** to make that arbitration
  decision efficiently.

Each coder alternates through four phases: waiting for dongles, compiling,
debugging and refactoring. Compiling requires **both** the coder's left and
right dongle at the same time. If a coder fails to start compiling again
within `time_to_burnout` milliseconds of their last compile, they **burn
out** and the whole simulation stops.

The program is single-binary, written in C, uses only POSIX threads and
mutexes/condition variables for synchronization (no busy-waiting on shared
state without a lock, no global variables).

## Instructions

### Build

```sh
cd coders
make            # builds ./codexion
make re         # clean rebuild
make clean      # remove object files
make fclean     # remove object files and the binary
```

The Makefile compiles with `-Wall -Wextra -Werror -pthread` using `cc`, and
never relinks unnecessarily (only what changed gets rebuilt).

### Run

```sh
./codexion number_of_coders time_to_burnout time_to_compile time_to_debug \
           time_to_refactor number_of_compiles_required dongle_cooldown scheduler
```

All 8 arguments are mandatory, all numeric arguments must be non-negative
integers (`number_of_coders` must additionally be >= 1), and `scheduler`
must be exactly `fifo` or `edf`. Any other input is rejected with an error
message and a non-zero exit code — nothing is guessed or defaulted.

Example:

```sh
./codexion 4 800 200 200 200 4 50 edf
```

Every state change is logged as:

```
timestamp_in_ms coder_id has taken a dongle
timestamp_in_ms coder_id is compiling
timestamp_in_ms coder_id is debugging
timestamp_in_ms coder_id is refactoring
timestamp_in_ms coder_id burned out
```

The simulation stops either when a coder burns out, or when every coder has
compiled at least `number_of_compiles_required` times.

## Resources

- *The Little Book of Semaphores* — Allen B. Downey (classic reference for
  the dining philosophers problem and resource-sharing patterns).
- `man pthread_mutex_lock`, `man pthread_cond_timedwait`, `man gettimeofday`
  — the exact POSIX semantics that the whole design leans on.
- Wikipedia — *Dining philosophers problem* and *Earliest deadline first
  scheduling*, for the general shape of the two classic policies asked for
  in this subject.

**AI usage:** an AI assistant (Claude) was used throughout this project as
a pair-programming partner, not as a black box that produced a finished
answer to copy in. Concretely it was used for:
- Discussing possible deadlock-avoidance strategies for the "two hands, one
  circle of shared resources" version of the problem before settling on the
  atomic-pair-acquisition design described below (an alternative discussed
  and rejected was the classic "odd/even pickup order" trick, since it does
  not naturally extend to a configurable `edf` policy).
- Writing and iterating on the C implementation itself, including finding
  and fixing a real concurrency bug during testing (see the cooldown note
  under *Blocking cases handled*).
- Running the actual test/verification tooling (compiling with strict
  flags, `valgrind --leak-check=full`, `helgrind`, and a separate
  ThreadSanitizer build) and iterating on the code based on their output.
- Checking the code against `norminette` and restructuring files to respect
  the 5-functions-per-file limit.

Every design decision below is something that can be explained and
defended independently of the tool that helped write it.

## Blocking cases handled

**Deadlock / Coffman conditions.** The classic dining-philosophers deadlock
(everyone picks up their left dongle and waits forever for their right one)
is avoided structurally, not by luck: a coder never holds one dongle while
waiting for the other. Both dongles for a compile are requested and granted
**atomically** under a single mutex (`sched_mutex`). A coder either gets
both dongles in the same critical section, or none at all and goes back to
waiting — so "hold and wait" (one of the four Coffman conditions) can never
happen, which removes the possibility of a circular wait entirely.

**Starvation prevention.** Simply granting dongles to "whoever asks first
each time" can let a request be repeatedly passed over by a stream of
smaller/luckier requests. To prevent this, every pending request carries a
priority `key` (arrival order for `fifo`, deadline for `edf`) stored in a
binary min-heap. A request is only granted once no other *conflicting*
pending request (one that needs one of the same two dongles) has a smaller
key. This guarantees older/more urgent requests are never permanently
overtaken by newer ones for a resource they are both waiting on.

**Cooldown handling — the bug we actually hit.** The first working version
used a plain `pthread_cond_wait` while waiting for dongles, woken only when
someone released a dongle. That is a real bug: a dongle's cooldown expires
on its own, with **no** release event to broadcast at that exact moment, so
threads could be woken once, see the dongle still cooling down, and then
sleep forever with nobody left to wake them — a live simulation that looks
like a deadlock. The fix was to switch to `pthread_cond_timedwait` with a
short (1 ms) bound, so every waiting coder also re-checks its condition
periodically on its own, independent of any broadcast. This was caught by
actually running the program (four coders got stuck after the very first
cycle) rather than by inspection alone.

**Burnout detection precision.** A dedicated **monitor thread** polls every
coder's deadline (`last_compile_start + time_to_burnout`) every 0.5 ms
(well under the 10 ms tolerance required) and is the only thread allowed to
print the `burned out` line and flip the global stop flag, guaranteeing
that message is never delayed by more than a couple of scheduler ticks past
the real deadline. Measured overshoot in testing was consistently 1 ms.

**Log serialization.** All prints (dongle/compile/debug/refactor/burnout)
go through `safe_print`, which holds a single `state_mutex` for the
"read stop flag + timestamp + printf" sequence, so two threads can never
interleave partial lines, and nothing prints after the simulation has
already been declared over.

## Thread synchronization mechanisms

- **`sched_mutex` + `sched_cond`** protect the array of dongles (busy flag,
  cooldown timestamp) and the pending-request heap. Every acquire/release
  of a dongle pair happens with this mutex held; `sched_cond` is
  broadcast whenever a dongle is released, and every waiter also wakes up
  on its own short timeout (via `pthread_cond_timedwait`) to notice
  cooldown expirations that no release event announces.
- **`state_mutex`** protects the single `stop` flag and all stdout output,
  so "check if we should still be running" and "print a line" are always
  observed as one atomic step by every thread (coders, monitor).
- **`compile_mutex`** protects each coder's `last_compile_start` and
  `compiles_done` counters, which are written by the coder's own thread and
  read concurrently by the monitor thread (for burnout deadlines) and by
  any coder finishing a compile (for the "everyone is done" check).
- Coders never talk to each other directly (as required by the subject);
  all coordination is mediated by these three mutexes plus the heap, which
  is exactly the "arbitrator" pattern for the dining philosophers problem —
  a coder only ever touches shared state while holding the relevant lock,
  and never sleeps on real time (`usleep`) while holding a mutex used by
  another thread's decision logic.
- Race-freedom was checked, not assumed: the release build passes
  `valgrind --leak-check=full` with zero leaks on every code path (normal
  completion, burnout, and the N=1 edge case that can never compile at
  all), and a separate build compiled with `-fsanitize=thread` reports zero
  races. `helgrind` reports two "lock not held" warnings that point
  directly at `pthread_cond_timedwait`; this is a documented Helgrind false
  positive for that specific function (Valgrind bug #392331), not a real
  issue — manual review confirms all three `pthread_cond_broadcast` call
  sites hold `sched_mutex`, and ThreadSanitizer (which does not share this
  limitation) found nothing.
