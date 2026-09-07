*This project has been created as part of the 42 curriculum by nfodere-.*

# Fly-In: Coordinated Drone Routing System

## Description

Fly-In is a multi-drone routing and turn-based simulation engine. Given
a text description of a network of **zones** connected by
bidirectional **links**, it computes collision-free, capacity-respecting
routes for a fleet of drones flying from a unique **start** zone to a
unique **end** zone, and prints the resulting movement schedule turn by
turn while trying to minimize the total number of simulation turns.

The engine has to respect several constraints at once:

- **Zone capacity** (`max_drones`): how many drones can sit in a zone
  during the same turn.
- **Link capacity** (`max_link_capacity`): how many drones can travel
  the same connection during the same turn.
- **Zone type costs**: `normal`/`priority` zones cost 1 turn to enter,
  `restricted` zones cost 2 turns and cannot be interrupted mid-flight,
  `blocked` zones can never be entered.
- **No collisions/deadlocks**: drones can wait in place when no legal
  move is available, and the scheduler is guaranteed to find a valid
  plan whenever one exists.

The whole project is **object-oriented**, **fully type-hinted**, and
uses **no external graph library** (only the Python standard library).

## Instructions

### Requirements

- Python 3.10+
- No third-party runtime dependency (only `flake8` and `mypy` are
  needed for linting, as dev tools).

### Installation

```bash
make install
```

Installs `flake8` and `mypy` for linting/type-checking. The simulator
itself has no runtime dependency.

### Running the simulation

```bash
make run                       # uses ./map.txt by default
make run MAP=maps/hard/02_capacity_hell.txt
python3 drone_system.py maps/medium/03_priority_puzzle.txt
```

Useful CLI flags:

| Flag          | Effect                                                      |
|---------------|---------------------------------------------------------------|
| `--gui`       | Also opens an animated Tk window (falls back gracefully to text-only if Tk isn't available). |
| `--no-color`  | Disables ANSI colors in the terminal output.                |
| `--summary`   | Prints secondary performance metrics after the run.          |

### Debugging

```bash
make debug                     # runs drone_system.py under pdb
```

### Linting / type-checking

```bash
make lint          # flake8 + mypy (subject-mandated flags)
make lint-strict    # flake8 + mypy --strict
```

### Tests (not graded, for local sanity checks only)

```bash
make test           # or: python3 -m unittest discover -s tests
```

### Cleaning

```bash
make clean
```

## Algorithm and Implementation Strategy

**Parsing.** `MapParser` reads the file line by line. Every directive
(`nb_drones:`, `start_hub:`, `end_hub:`, `hub:`, `connection:`) is
validated individually and any problem raises a `MapParseError` that
names the exact line and the cause (unknown zone type, duplicate zone
or connection, undefined zone reference, malformed metadata, etc.),
so the program never crashes on a bad input file — it reports a clear
error and exits with status 1 instead.

**Routing.** Each drone's route is computed with a **time-expanded
A\*** search: a search state is `(zone, turn)` instead of just `zone`,
so the algorithm naturally reasons about *when* a drone would be
somewhere, not only *where*. From any state the drone can:

- **wait** one turn in its current zone (if it still has capacity),
- **move** to a neighbouring `normal`/`priority` zone (1 turn), or
- **start a `restricted` transit**, which reserves the connection for
  *two consecutive turns* and cannot be interrupted or resumed later
  (exactly as required by the subject).

A backward Dijkstra pass from the end zone (ignoring capacities)
precomputes a heuristic for every zone; `priority` zones get a
slightly discounted heuristic/step weight so that, among routes of
equal real turn-cost, the search favors the ones going through
`priority` zones — without ever changing the *real* simulated turn
count, which always advances by exactly 1 (normal/priority) or 2
(restricted) turns.

**Multi-drone coordination.** Drones are planned **one at a time, in
ID order**, against a single shared `ReservationTable` (a classic
*prioritized planning* / *cooperative A\** strategy): drone 1 gets the
best possible route, drone 2's search must respect every zone/link
reservation drone 1 already made, and so on. Because *waiting* is a
first-class action inside the search itself, a single search call per
drone is always enough — the algorithm naturally staggers departures
and routes around congestion instead of needing external retry loops.
This is not guaranteed to find the global optimum (that would require
jointly optimizing every drone's path, which is combinatorially much
more expensive), but it is fast, always finds a solution when one
exists, and comfortably beats every benchmark in the subject (see
below).

**Complexity.** For one drone, the search explores at most
`O(V x T)` states (`V` = number of zones, `T` = turns needed), each
with `O(deg(v))` expansions, so a single drone's search is
`O(V x T x deg)` with a binary heap (`O(log(V*T))` per push/pop). For
`N` drones planned sequentially, the total cost is `O(N x V x T x
deg x log(V*T))`. Nothing is recomputed from scratch beyond that: the
per-zone heuristic is cached once (`PathFinder.__init__`), and the
reservation table only ever grows by the turns actually reserved
(memory is `O(total turns reserved across all drones)`, not
`O(V x T)`), so memory stays proportional to the length of the
final schedule rather than to the search horizon.

**Output.** `SimulationEngine` renders one line per turn (only drones
that move that turn are printed, exactly as required), with an
optional `--summary` block reporting secondary metrics (total turns,
drones delivered, average turns/drone, total weighted path cost).

## Visual Representation

Two complementary layers, as allowed by the subject:

- **Colored terminal output (always on).** Every printed move
  (`D<id>-<zone>` / `D<id>-<connection>`) is colored using that zone's
  declared `color=` metadata (mapped to the closest ANSI code), so at
  a glance you can see which drones are moving through which kind of
  zone each turn. Use `--no-color` to disable it (e.g. for piping to a
  file).
- **Optional animated Tk GUI (`--gui`).** Draws the whole network
  (zones as colored nodes at their `x, y` coordinates, connections as
  lines) with playback controls — Play/Pause, step forward/back, and
  a scrubber slider to jump to any turn — instead of a fixed
  auto-play. The layout is **fully responsive**: node positions and
  node radius are recomputed from the *live* canvas size on every
  resize, and the radius automatically shrinks on dense maps so
  nodes and labels never overlap. Zone type is encoded visually (a
  dashed orange outline for `restricted`, gold for `priority`, green
  ring for the start hub, red ring for the end hub), and the
  connection currently being traversed is highlighted in blue. A
  legend at the bottom explains all of this. It is entirely optional:
  if `tkinter` is not installed, the program prints a short notice
  and keeps working in text-only mode instead of crashing — this was
  one of the main robustness bugs fixed in this version (see below).

Together they make it easy to both *machine-check* the output (plain
text format, parseable) and *eyeball* it (color/animation) to sanity
check that a schedule looks reasonable.

## Example Input and Output

Input (`maps/easy/01_linear_path.txt`):

```
nb_drones: 2
start_hub: start 0 0 [color=green]
hub: waypoint1 1 0 [color=blue]
hub: waypoint2 2 0 [color=blue]
end_hub: goal 3 0 [color=red]
connection: start-waypoint1
connection: waypoint1-waypoint2
connection: waypoint2-goal
```

Command:

```bash
python3 drone_system.py maps/easy/01_linear_path.txt --no-color --summary
```

Output:

```
D1-waypoint1
D1-waypoint2 D2-waypoint1
D1-goal D2-waypoint2
D2-goal
--- Summary ---
Total simulation turns : 4
Drones delivered       : 2
Average turns per drone: 3.50
Total weighted path cost: 6.0
```

A restricted-zone example — two drones sharing a single-capacity
`restricted` link correctly serialize instead of overlapping (from
`maps/custom/04_restricted_queue.txt`):

```
D1-start-tunnel
D1-tunnel
D1-goal D2-start-tunnel
D2-tunnel
D2-goal
```

## Performance vs. the Subject's Benchmarks

Measured with `--no-color` on the maps shipped in `maps/`:

| Map                                   | Target       | Result   |
|----------------------------------------|--------------|----------|
| Easy: linear path (2 drones)           | <= 6 turns   | 4 turns  |
| Easy: simple fork (4 drones)           | <= 8 turns   | 4 turns  |
| Easy: basic capacity (4 drones)        | <= 6 turns   | 4 turns  |
| Medium: dead end trap (5 drones)       | <= 12 turns  | 8 turns  |
| Medium: circular loop (6 drones)       | <= 15 turns  | 15 turns |
| Medium: priority puzzle (5 drones)     | <= 12 turns  | 7 turns  |
| Hard: maze nightmare (8 drones)        | <= 30 turns  | 13 turns |
| Hard: capacity hell (12 drones)        | <= 35 turns  | 16 turns |
| Hard: ultimate challenge (15 drones)   | <= 45 turns  | 26 turns |
| Challenger: The Impossible Dream (25)  | beat 45 (optional) | **43 turns** |

All maps solve in well under 100 ms.

## Custom Maps

On top of the maps provided with the subject, `maps/custom/` contains
a handful of maps written specifically to exercise edge cases and
error handling while working on this project:

- `01_blocked_detour.txt` — a `blocked` zone that must be routed
  around.
- `02_single_drone_capacity1.txt` — the smallest possible valid map.
- `03_shared_bottleneck.txt` — six drones funneled through a single
  `max_drones=1` hub (strict serialization).
- `04_restricted_queue.txt` — two drones queuing for the same
  `restricted` (2-turn) connection.
- `05_unreachable_goal.txt` — a topologically unreachable goal, to
  check the program fails cleanly (exit code 1, clear message)
  instead of hanging or crashing.

## Resources

- Python documentation:
  [`heapq`](https://docs.python.org/3/library/heapq.html),
  [`dataclasses`](https://docs.python.org/3/library/dataclasses.html),
  [`enum`](https://docs.python.org/3/library/enum.html),
  [`argparse`](https://docs.python.org/3/library/argparse.html),
  [`typing`](https://docs.python.org/3/library/typing.html).
- Amit Patel / Red Blob Games,
  [Introduction to A*](https://www.redblobgames.com/pathfinding/a-star/introduction.html),
  for the general A* refresher.
- D. Silver, *Cooperative Pathfinding* (AIIDE 2005) — background on
  prioritized/cooperative multi-agent pathfinding, the family of
  technique this project's sequential drone scheduling belongs to.
- [`flake8`](https://flake8.pycqa.org/) and
  [`mypy`](https://mypy.readthedocs.io/) documentation, for the
  linting/type-checking setup required by the subject.

### AI usage:
AI has been used to search for information, fix bugs, and run tests.
