#!/usr/bin/env python3
"""Fly-In: multi-drone routing and turn-based simulation engine.

This module reads a text description of a network of "zones" linked
by bidirectional "connections", then computes collision-free,
capacity-respecting routes for a fleet of drones from a unique start
zone to a unique end zone, minimizing the total number of simulation
turns needed to deliver every drone.

The whole pipeline is object-oriented and dependency-free (standard
library only, no graph libraries): a :class:`MapParser` builds a
:class:`NetworkGraph`, a :class:`PathFinder` performs a time-expanded
A* search for each drone against a shared :class:`ReservationTable`,
and :class:`SimulationEngine` turns the resulting plans into the
required turn-by-turn textual output (plus an optional Tk GUI).
"""

from __future__ import annotations

import argparse
import heapq
import itertools
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def pair_key(zone_a: str, zone_b: str) -> Tuple[str, str]:
    """Return an order-independent identity for an unordered pair.

    Used to key connection bookings so that traversing a link in
    either direction always maps to the same reservation bucket.
    """
    return (zone_a, zone_b) if zone_a <= zone_b else (zone_b, zone_a)


# ---------------------------------------------------------------------
# Domain model
# ---------------------------------------------------------------------


class MapParseError(ValueError):
    """Raised when the input map file is syntactically or semantically
    invalid.

    The message always embeds the offending line number so users can
    fix their map file quickly.
    """

    def __init__(self, line_no: Optional[int], message: str) -> None:
        """Build a parse error tied to a specific input line.

        Args:
            line_no: 1-indexed line number where the issue was found,
                or ``None`` for file-level errors.
            message: Human readable explanation of the problem.
        """
        prefix = f"Line {line_no}: " if line_no is not None else ""
        super().__init__(f"{prefix}{message}")
        self.line_no = line_no


class ZoneType(str, Enum):
    """The four zone kinds supported by the map format."""

    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"

    @classmethod
    def from_raw(cls, raw: str, line_no: int) -> "ZoneType":
        """Parse a zone type token, raising :class:`MapParseError`.

        Args:
            raw: The raw ``zone=<value>`` token value.
            line_no: Line number, used for the error message.
        """
        try:
            return cls(raw)
        except ValueError as exc:
            allowed = ", ".join(member.value for member in cls)
            raise MapParseError(
                line_no,
                f"unknown zone type '{raw}' (expected one of {allowed})",
            ) from exc

    @property
    def travel_turns(self) -> int:
        """Number of simulation turns needed to move into this zone."""
        return 2 if self is ZoneType.RESTRICTED else 1

    @property
    def search_weight(self) -> float:
        """Cost used by the pathfinder's priority queue.

        Equal to :attr:`travel_turns` for every zone type except
        ``priority``, which is given a discount so that the A* search
        prefers routes going through priority zones when several
        routes take the same real number of turns. This discount only
        affects path *selection*, never the real simulated turn count
        (see :attr:`travel_turns`, which is always used for the
        actual clock).
        """
        if self is ZoneType.PRIORITY:
            return 0.5
        return float(self.travel_turns)


@dataclass
class Zone:
    """A single node ("hub") of the drone network."""

    name: str
    x: int
    y: int
    zone_type: ZoneType = ZoneType.NORMAL
    color: Optional[str] = None
    max_drones: int = 1
    is_start: bool = False
    is_end: bool = False

    @property
    def has_unlimited_capacity(self) -> bool:
        """Whether this zone ignores ``max_drones`` (start/end)."""
        return self.is_start or self.is_end


@dataclass
class Connection:
    """A bidirectional link between two zones."""

    zone_a: str
    zone_b: str
    max_link_capacity: int = 1

    def other(self, zone_name: str) -> str:
        """Return the endpoint opposite to ``zone_name``."""
        if zone_name == self.zone_a:
            return self.zone_b
        if zone_name == self.zone_b:
            return self.zone_a
        raise ValueError(f"'{zone_name}' is not part of this connection")

    @property
    def key(self) -> Tuple[str, str]:
        """Order-independent identity used for capacity bookkeeping."""
        return pair_key(self.zone_a, self.zone_b)


class NetworkGraph:
    """The full zone/connection graph plus adjacency lookups."""

    def __init__(self) -> None:
        """Create an empty network."""
        self.zones: Dict[str, Zone] = {}
        self.connections: List[Connection] = []
        self.adjacency: Dict[str, List[Connection]] = {}
        self.start_zone: Optional[str] = None
        self.end_zone: Optional[str] = None

    def add_zone(self, zone: Zone, line_no: int) -> None:
        """Register a new zone, enforcing uniqueness constraints."""
        if zone.name in self.zones:
            raise MapParseError(
                line_no, f"duplicate zone name '{zone.name}'"
            )
        if zone.is_start:
            if self.start_zone is not None:
                raise MapParseError(line_no, "multiple start_hub zones")
            self.start_zone = zone.name
        if zone.is_end:
            if self.end_zone is not None:
                raise MapParseError(line_no, "multiple end_hub zones")
            self.end_zone = zone.name
        self.zones[zone.name] = zone
        self.adjacency[zone.name] = []

    def add_connection(self, conn: Connection, line_no: int) -> None:
        """Register a bidirectional connection between two zones."""
        if conn.zone_a == conn.zone_b:
            raise MapParseError(
                line_no, f"self-loop connection on '{conn.zone_a}'"
            )
        if conn.zone_a not in self.zones or conn.zone_b not in self.zones:
            raise MapParseError(
                line_no,
                f"connection '{conn.zone_a}-{conn.zone_b}' references "
                "an undefined zone",
            )
        self.connections.append(conn)
        self.adjacency[conn.zone_a].append(conn)
        self.adjacency[conn.zone_b].append(conn)

    def neighbours(self, zone_name: str) -> List[Connection]:
        """Return every connection touching ``zone_name``."""
        return self.adjacency.get(zone_name, [])


# ---------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------


class MapParser:
    """Parses and validates a Fly-In map description file."""

    _ZONE_PREFIXES = ("start_hub:", "end_hub:", "hub:")
    _VALID_ZONE_META_KEYS = {"zone", "color", "max_drones"}
    _VALID_CONN_META_KEYS = {"max_link_capacity"}

    @classmethod
    def parse(cls, filepath: str) -> Tuple[int, NetworkGraph]:
        """Parse ``filepath`` into a drone count and a network graph.

        Args:
            filepath: Path to the map description file.

        Returns:
            A tuple ``(nb_drones, network)``.

        Raises:
            MapParseError: On any structural or semantic violation.
        """
        try:
            raw_lines = Path(filepath).read_text(encoding="utf-8")
        except OSError as exc:
            raise MapParseError(
                None, f"cannot read map file '{filepath}': {exc}"
            ) from exc

        network = NetworkGraph()
        nb_drones: Optional[int] = None
        seen_connections: set[Tuple[str, str]] = set()
        first_directive_seen = False

        for line_no, raw_line in enumerate(raw_lines.splitlines(), 1):
            line = raw_line.split("#", 1)[0].strip()
            if not line:
                continue

            if line.startswith("nb_drones:"):
                if first_directive_seen:
                    raise MapParseError(
                        line_no,
                        "'nb_drones:' must be the first directive in "
                        "the file",
                    )
                if nb_drones is not None:
                    raise MapParseError(
                        line_no, "'nb_drones:' declared more than once"
                    )
                nb_drones = cls._parse_nb_drones(line, line_no)
                first_directive_seen = True
                continue

            first_directive_seen = True
            if line.startswith(cls._ZONE_PREFIXES):
                cls._parse_zone_line(line, line_no, network)
                continue

            if line.startswith("connection:"):
                cls._parse_connection_line(
                    line, line_no, network, seen_connections
                )
                continue

            raise MapParseError(line_no, f"unrecognized directive: {line!r}")

        if nb_drones is None:
            raise MapParseError(None, "missing mandatory 'nb_drones:' line")
        if network.start_zone is None or network.end_zone is None:
            raise MapParseError(
                None, "the map must define exactly one start_hub and "
                "one end_hub"
            )
        return nb_drones, network

    @staticmethod
    def _parse_nb_drones(line: str, line_no: int) -> int:
        raw = line[len("nb_drones:"):].strip()
        if not raw.isdigit():
            raise MapParseError(
                line_no, "'nb_drones:' expects a positive integer"
            )
        value = int(raw)
        if value <= 0:
            raise MapParseError(
                line_no, "'nb_drones:' must be a positive integer"
            )
        return value

    @staticmethod
    def _split_metadata(rem: str, line_no: int) -> Tuple[str, Dict[str, str]]:
        """Split ``name x y`` from an optional ``[k=v ...]`` block."""
        meta: Dict[str, str] = {}
        bracket_start = rem.find("[")
        if bracket_start != -1:
            if not rem.endswith("]"):
                raise MapParseError(line_no, "malformed metadata block")
            body = rem[bracket_start + 1: -1]
            head = rem[:bracket_start].strip()
            for token in body.split():
                if "=" not in token:
                    raise MapParseError(
                        line_no, f"malformed metadata token '{token}'"
                    )
                key, _, value = token.partition("=")
                if key in meta:
                    raise MapParseError(
                        line_no, f"duplicate metadata key '{key}'"
                    )
                meta[key] = value
            return head, meta
        return rem.strip(), meta

    @classmethod
    def _parse_zone_line(
        cls, line: str, line_no: int, network: NetworkGraph
    ) -> None:
        prefix, _, rem = line.partition(":")
        prefix = f"{prefix}:"
        head, meta = cls._split_metadata(rem.strip(), line_no)

        tokens = head.split()
        if len(tokens) != 3:
            raise MapParseError(
                line_no, "expected '<name> <x> <y>' for a zone definition"
            )
        name, x_str, y_str = tokens
        if "-" in name or not name:
            raise MapParseError(
                line_no, f"invalid zone name '{name}' (dashes forbidden)"
            )
        try:
            x, y = int(x_str), int(y_str)
        except ValueError as exc:
            raise MapParseError(
                line_no, "zone coordinates must be integers"
            ) from exc

        is_start = prefix == "start_hub:"
        is_end = prefix == "end_hub:"

        for key in meta:
            if key not in cls._VALID_ZONE_META_KEYS:
                raise MapParseError(
                    line_no, f"unknown zone metadata key '{key}'"
                )

        zone_type = ZoneType.NORMAL
        if "zone" in meta:
            zone_type = ZoneType.from_raw(meta["zone"], line_no)

        color = meta.get("color")

        # Per the subject, max_drones is ignored (never validated) on
        # the start/end hubs: those zones have unlimited capacity.
        max_drones = 1
        if "max_drones" in meta and not (is_start or is_end):
            raw_cap = meta["max_drones"]
            if not raw_cap.isdigit() or int(raw_cap) <= 0:
                raise MapParseError(
                    line_no, "'max_drones' must be a positive integer"
                )
            max_drones = int(raw_cap)

        zone = Zone(
            name=name,
            x=x,
            y=y,
            zone_type=zone_type,
            color=color,
            max_drones=max_drones,
            is_start=is_start,
            is_end=is_end,
        )
        network.add_zone(zone, line_no)

    @classmethod
    def _parse_connection_line(
        cls,
        line: str,
        line_no: int,
        network: NetworkGraph,
        seen: set[Tuple[str, str]],
    ) -> None:
        rem = line[len("connection:"):].strip()
        head, meta = cls._split_metadata(rem, line_no)

        if "-" not in head:
            raise MapParseError(line_no, "expected '<zone1>-<zone2>'")
        zone_a, _, zone_b = head.partition("-")
        zone_a, zone_b = zone_a.strip(), zone_b.strip()
        if not zone_a or not zone_b or "-" in zone_b:
            raise MapParseError(line_no, "expected '<zone1>-<zone2>'")

        for key in meta:
            if key not in cls._VALID_CONN_META_KEYS:
                raise MapParseError(
                    line_no, f"unknown connection metadata key '{key}'"
                )

        max_capacity = 1
        if "max_link_capacity" in meta:
            raw_cap = meta["max_link_capacity"]
            if not raw_cap.isdigit() or int(raw_cap) <= 0:
                raise MapParseError(
                    line_no, "'max_link_capacity' must be a positive "
                    "integer"
                )
            max_capacity = int(raw_cap)

        norm_key = pair_key(zone_a, zone_b)
        if norm_key in seen:
            raise MapParseError(
                line_no, f"duplicate connection '{zone_a}-{zone_b}'"
            )
        seen.add(norm_key)

        connection = Connection(zone_a, zone_b, max_capacity)
        network.add_connection(connection, line_no)


# ---------------------------------------------------------------------
# Simulation planning
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class PlanStep:
    """One turn's worth of action performed by a single drone.

    Attributes:
        turn: The 1-indexed simulation turn this step happens on.
        label: What to print for this turn (``D<id>-<label>``), or
            ``None`` if the drone does not move (waiting) and should
            therefore be omitted from that turn's output line.
        zone_hold: The zone whose capacity is consumed at this turn,
            or ``None`` while the drone is mid-flight on a restricted
            connection.
        link_hold: The connection (as an unordered pair) whose
            capacity is consumed at this turn, or ``None``.
    """

    turn: int
    label: Optional[str]
    zone_hold: Optional[str]
    link_hold: Optional[Tuple[str, str]] = None


@dataclass
class Drone:
    """A drone identified by an integer id and its computed plan."""

    drone_id: int
    plan: List[PlanStep] = field(default_factory=list)

    @property
    def arrival_turn(self) -> int:
        """Turn at which this drone reaches the end zone."""
        return self.plan[-1].turn if self.plan else 0

    @property
    def path_cost(self) -> float:
        """Sum of the weighted movement costs along this drone's path."""
        cost = 0.0
        for step in self.plan:
            if step.zone_hold is not None:
                cost += 1.0
        return cost


class ReservationTable:
    """Tracks per-turn occupancy of zones and connections.

    Booking a :class:`PlanStep` and later checking availability always
    goes through the *same* ``(location, turn)`` key, which is what
    makes the capacity accounting exact and symmetric for both
    single-turn moves and two-turn restricted transits.
    """

    def __init__(self, network: NetworkGraph) -> None:
        """Initialize an empty reservation table for ``network``."""
        self.network = network
        self._zone_bookings: Dict[str, Dict[int, int]] = {}
        self._link_bookings: Dict[Tuple[str, str], Dict[int, int]] = {}

    def is_zone_free(self, zone_name: str, turn: int) -> bool:
        """Whether ``zone_name`` has spare capacity at ``turn``."""
        zone = self.network.zones[zone_name]
        if zone.has_unlimited_capacity:
            return True
        if zone.zone_type is ZoneType.BLOCKED:
            return False
        booked = self._zone_bookings.get(zone_name, {}).get(turn, 0)
        return booked < zone.max_drones

    def is_link_free(self, zone_a: str, zone_b: str, turn: int) -> bool:
        """Whether the connection between two zones is free at ``turn``."""
        key = pair_key(zone_a, zone_b)
        capacity = 1
        for conn in self.network.neighbours(zone_a):
            if conn.other(zone_a) == zone_b:
                capacity = conn.max_link_capacity
                break
        booked = self._link_bookings.get(key, {}).get(turn, 0)
        return booked < capacity

    def reserve(self, plan: List[PlanStep]) -> None:
        """Permanently book every resource used by ``plan``."""
        for step in plan:
            if step.zone_hold is not None:
                per_turn = self._zone_bookings.setdefault(
                    step.zone_hold, {}
                )
                per_turn[step.turn] = per_turn.get(step.turn, 0) + 1
            if step.link_hold is not None:
                key = pair_key(*step.link_hold)
                per_turn_link = self._link_bookings.setdefault(key, {})
                per_turn_link[step.turn] = (
                    per_turn_link.get(step.turn, 0) + 1
                )


class PathFinder:
    """Time-expanded A* search for a single drone's optimal plan."""

    #: Safety cap on how many turns ahead the search is allowed to
    #: look, preventing an unbounded search on an unsolvable map.
    MAX_HORIZON = 3000

    def __init__(self, network: NetworkGraph) -> None:
        """Pre-compute a goal-distance heuristic over ``network``."""
        self.network = network
        self._heuristic = self._compute_heuristic()
        self._tie_breaker = itertools.count()

    def _compute_heuristic(self) -> Dict[str, float]:
        """Backward Dijkstra from the end zone, ignoring capacities.

        Gives every zone a lower-bound-ish estimate (in the same
        priority/restricted-weighted unit as the search cost) of how
        far it is from the goal, used to focus the A* search.
        """
        end = self.network.end_zone
        distances: Dict[str, float] = {}
        if end is None:
            return distances
        distances[end] = 0.0
        heap: List[Tuple[float, str]] = [(0.0, end)]
        while heap:
            dist, node = heapq.heappop(heap)
            if dist > distances.get(node, float("inf")):
                continue
            for conn in self.network.neighbours(node):
                neighbour = conn.other(node)
                n_zone = self.network.zones[neighbour]
                if n_zone.zone_type is ZoneType.BLOCKED:
                    continue
                new_dist = dist + n_zone.zone_type.search_weight
                if new_dist < distances.get(neighbour, float("inf")):
                    distances[neighbour] = new_dist
                    heapq.heappush(heap, (new_dist, neighbour))
        return distances

    def _heuristic_value(self, zone_name: str) -> float:
        return self._heuristic.get(zone_name, 0.0)

    def find_path(
        self, table: ReservationTable
    ) -> Optional[List[PlanStep]]:
        """Find the best available plan given current reservations.

        Waiting is a first-class search action, so a single search
        from turn 0 is enough: the drone will "wait" as many turns as
        needed at any congested zone along the way instead of never
        finding a route.

        Returns:
            The ordered list of :class:`PlanStep`, or ``None`` if no
            feasible route exists within :attr:`MAX_HORIZON` turns.
        """
        start = self.network.start_zone
        end = self.network.end_zone
        if start is None or end is None:
            return None

        Entry = Tuple[float, float, int, str, int, Tuple[PlanStep, ...]]
        BestG = Dict[Tuple[str, int], float]
        start_h = self._heuristic_value(start)
        open_heap: List[Entry] = [
            (start_h, 0.0, next(self._tie_breaker), start, 0, ())
        ]
        best_g: BestG = {(start, 0): 0.0}

        while open_heap:
            _, g_cost, _, zone, turn, plan = heapq.heappop(open_heap)

            if zone == end:
                return list(plan)
            if turn > self.MAX_HORIZON:
                continue
            if g_cost > best_g.get((zone, turn), float("inf")):
                continue  # stale heap entry, a better one was found

            self._expand_wait(
                table, zone, turn, g_cost, plan, open_heap, best_g
            )
            self._expand_moves(
                table, zone, turn, g_cost, plan, open_heap, best_g
            )

        return None

    def _push(
        self,
        open_heap: List[
            Tuple[float, float, int, str, int, Tuple[PlanStep, ...]]
        ],
        best_g: Dict[Tuple[str, int], float],
        zone: str,
        turn: int,
        g_cost: float,
        plan: Tuple[PlanStep, ...],
    ) -> None:
        """Push a candidate state, pruning dominated duplicates."""
        key = (zone, turn)
        if g_cost >= best_g.get(key, float("inf")):
            return
        best_g[key] = g_cost
        h_cost = self._heuristic_value(zone)
        heapq.heappush(
            open_heap,
            (g_cost + h_cost, g_cost, next(self._tie_breaker), zone,
             turn, plan),
        )

    def _expand_wait(
        self,
        table: ReservationTable,
        zone: str,
        turn: int,
        g_cost: float,
        plan: Tuple[PlanStep, ...],
        open_heap: List[
            Tuple[float, float, int, str, int, Tuple[PlanStep, ...]]
        ],
        best_g: Dict[Tuple[str, int], float],
    ) -> None:
        if not table.is_zone_free(zone, turn + 1):
            return
        step = PlanStep(turn=turn + 1, label=None, zone_hold=zone)
        new_plan = plan + (step,)
        self._push(open_heap, best_g, zone, turn + 1, g_cost + 1.0,
                   new_plan)

    def _expand_moves(
        self,
        table: ReservationTable,
        zone: str,
        turn: int,
        g_cost: float,
        plan: Tuple[PlanStep, ...],
        open_heap: List[
            Tuple[float, float, int, str, int, Tuple[PlanStep, ...]]
        ],
        best_g: Dict[Tuple[str, int], float],
    ) -> None:
        for conn in self.network.neighbours(zone):
            neighbour = conn.other(zone)
            n_zone = self.network.zones[neighbour]
            if n_zone.zone_type is ZoneType.BLOCKED:
                continue

            if n_zone.zone_type is ZoneType.RESTRICTED:
                self._expand_restricted(
                    table, zone, neighbour, turn, g_cost, plan, open_heap,
                    best_g,
                )
            else:
                self._expand_simple(
                    table, zone, neighbour, n_zone, turn, g_cost, plan,
                    open_heap, best_g,
                )

    def _expand_simple(
        self,
        table: ReservationTable,
        zone: str,
        neighbour: str,
        n_zone: Zone,
        turn: int,
        g_cost: float,
        plan: Tuple[PlanStep, ...],
        open_heap: List[
            Tuple[float, float, int, str, int, Tuple[PlanStep, ...]]
        ],
        best_g: Dict[Tuple[str, int], float],
    ) -> None:
        if not table.is_link_free(zone, neighbour, turn + 1):
            return
        if not table.is_zone_free(neighbour, turn + 1):
            return
        step = PlanStep(
            turn=turn + 1,
            label=neighbour,
            zone_hold=neighbour,
            link_hold=(zone, neighbour),
        )
        new_plan = plan + (step,)
        self._push(
            open_heap, best_g, neighbour, turn + 1,
            g_cost + n_zone.zone_type.search_weight, new_plan,
        )

    def _expand_restricted(
        self,
        table: ReservationTable,
        zone: str,
        neighbour: str,
        turn: int,
        g_cost: float,
        plan: Tuple[PlanStep, ...],
        open_heap: List[
            Tuple[float, float, int, str, int, Tuple[PlanStep, ...]]
        ],
        best_g: Dict[Tuple[str, int], float],
    ) -> None:
        first_turn = turn + 1
        second_turn = turn + 2
        if not table.is_link_free(zone, neighbour, first_turn):
            return
        if not table.is_link_free(zone, neighbour, second_turn):
            return
        if not table.is_zone_free(neighbour, second_turn):
            return
        transit_step = PlanStep(
            turn=first_turn,
            label=f"{zone}-{neighbour}",
            zone_hold=None,
            link_hold=(zone, neighbour),
        )
        arrival_step = PlanStep(
            turn=second_turn,
            label=neighbour,
            zone_hold=neighbour,
            link_hold=(zone, neighbour),
        )
        new_plan = plan + (transit_step, arrival_step)
        self._push(
            open_heap, best_g, neighbour, second_turn,
            g_cost + ZoneType.RESTRICTED.search_weight, new_plan,
        )


# ---------------------------------------------------------------------
# Presentation layer
# ---------------------------------------------------------------------


class Visualizer:
    """Maps map-file color names to ANSI terminal escape codes."""

    _PALETTE: Dict[str, str] = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "gray": "\033[90m",
        "grey": "\033[90m",
        "white": "\033[97m",
        "orange": "\033[38;5;208m",
        "purple": "\033[38;5;135m",
    }
    _RESET = "\033[0m"

    def __init__(self, enabled: bool = True) -> None:
        """Create a visualizer; ``enabled=False`` disables all color."""
        self.enabled = enabled

    def colorize(self, text: str, color: Optional[str]) -> str:
        """Wrap ``text`` in the ANSI code for ``color`` if known."""
        if not self.enabled or not color:
            return text
        code = self._PALETTE.get(color.lower())
        if not code:
            return text
        return f"{code}{text}{self._RESET}"


class SimulationResult:
    """Bundles the outcome of a completed simulation run."""

    def __init__(self, drones: List[Drone]) -> None:
        """Store the per-drone plans and derive the total turn count."""
        self.drones = drones
        self.total_turns = max(
            (drone.arrival_turn for drone in drones), default=0
        )


class SimulationEngine:
    """Coordinates parsing, pathfinding and turn-by-turn reporting."""

    def __init__(self, nb_drones: int, network: NetworkGraph) -> None:
        """Prepare a simulation for ``nb_drones`` drones over ``network``."""
        self.nb_drones = nb_drones
        self.network = network
        self.pathfinder = PathFinder(network)

    def plan(self) -> SimulationResult:
        """Compute a collision-free plan for every drone in turn order.

        Drones are planned one at a time, in id order (a classic
        "prioritized planning" strategy): each new drone's search
        respects every reservation already made by earlier drones.
        This scales well and, combined with waiting as a first-class
        action, always finds a valid schedule whenever one exists.
        """
        table = ReservationTable(self.network)
        drones: List[Drone] = []
        for drone_id in range(1, self.nb_drones + 1):
            found_plan = self.pathfinder.find_path(table)
            if found_plan is None:
                raise RuntimeError(
                    f"No feasible route could be found for drone "
                    f"D{drone_id} given the current map and "
                    "reservations."
                )
            table.reserve(found_plan)
            drones.append(Drone(drone_id=drone_id, plan=found_plan))
        return SimulationResult(drones)

    def render_text(
        self, result: SimulationResult, visualizer: Visualizer
    ) -> List[str]:
        """Render the turn-by-turn textual simulation output."""
        lines: List[str] = []
        for turn in range(1, result.total_turns + 1):
            actions: List[str] = []
            for drone in result.drones:
                for step in drone.plan:
                    if step.turn != turn or step.label is None:
                        continue
                    color = self._color_for_label(step.label)
                    move = visualizer.colorize(
                        f"D{drone.drone_id}-{step.label}", color
                    )
                    actions.append(move)
                    break
            if actions:
                lines.append(" ".join(actions))
        return lines

    def _color_for_label(self, label: str) -> Optional[str]:
        zone = self.network.zones.get(label)
        return zone.color if zone else None

    def render_summary(self, result: SimulationResult) -> List[str]:
        """Render the optional secondary performance metrics."""
        nb_drones = len(result.drones) or 1
        total_cost = sum(drone.path_cost for drone in result.drones)
        avg_turns = (
            sum(drone.arrival_turn for drone in result.drones) / nb_drones
        )
        return [
            "--- Summary ---",
            f"Total simulation turns : {result.total_turns}",
            f"Drones delivered       : {len(result.drones)}",
            f"Average turns per drone: {avg_turns:.2f}",
            f"Total weighted path cost: {total_cost:.1f}",
        ]


# ---------------------------------------------------------------------
# Optional Tk GUI (never required for the simulation to run)
# ---------------------------------------------------------------------


class GuiEngine:
    """Optional graphical, animated view of the simulation.

    The layout is fully responsive: on every resize (or turn change)
    node positions and node radius are recomputed from the *current*
    canvas size and from the actual spacing between zones, so nodes
    and labels never overlap regardless of window size or how dense
    the map is. Playback is controlled (play/pause, step, scrub)
    instead of free-running, so a turn can be inspected at leisure.
    """

    #: Reserved margin (pixels) around the drawable area, for labels.
    _MARGIN_X = 70
    _MARGIN_Y = 60
    #: Node radius bounds (pixels), adapted to the available space.
    _MIN_RADIUS = 9.0
    _MAX_RADIUS = 30.0

    def __init__(
        self,
        network: NetworkGraph,
        result: SimulationResult,
        frame_delay_ms: int = 700,
    ) -> None:
        """Build the Tk window; call :meth:`run` to start the animation."""
        import tkinter as tk  # local import: tkinter may be absent

        self._tk = tk
        self.network = network
        self.result = result
        self.frame_delay_ms = frame_delay_ms
        self.current_turn = 1
        self.playing = False
        self._safe_colors: Dict[str, str] = {}

        self.root = tk.Tk()
        self.root.title("Fly-In: Drone Routing Simulation")
        self.root.geometry("1050x720")
        self.root.minsize(560, 420)
        self.root.configure(bg="#1b1b1f")

        self._build_control_bar()
        self.canvas = tk.Canvas(self.root, bg="#141417",
                                highlightthickness=0)
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self._build_legend()

        self.canvas.bind("<Configure>", lambda _e: self._render_frame())

    def run(self) -> None:
        """Start the Tk animation loop (blocking call)."""
        self.root.update_idletasks()
        self._render_frame()
        self.root.mainloop()

    # -- UI construction -------------------------------------------------

    def _build_control_bar(self) -> None:
        tk = self._tk
        bar = tk.Frame(self.root, bg="#25252b")
        bar.pack(side=tk.TOP, fill=tk.X)

        self.turn_label = tk.Label(
            bar, text="", font=("Helvetica", 12, "bold"),
            fg="white", bg="#25252b",
        )
        self.turn_label.pack(side=tk.LEFT, padx=(12, 16), pady=8)

        self.play_button = tk.Button(
            bar, text="\u25b6 Play", width=9, command=self._toggle_play
        )
        self.play_button.pack(side=tk.LEFT, padx=3)
        tk.Button(
            bar, text="\u25c0\u25c0", width=4, command=self._step_back
        ).pack(side=tk.LEFT, padx=3)
        tk.Button(
            bar, text="\u25b6\u25b6", width=4, command=self._step_forward
        ).pack(side=tk.LEFT, padx=3)

        max_turn = max(1, self.result.total_turns)
        self.turn_scale = tk.Scale(
            bar, from_=1, to=max_turn, orient=tk.HORIZONTAL,
            showvalue=False, command=self._on_scale,
            bg="#25252b", fg="white", troughcolor="#3a3a42",
            highlightthickness=0,
        )
        self.turn_scale.pack(side=tk.LEFT, padx=12, fill=tk.X, expand=True)

    def _build_legend(self) -> None:
        tk = self._tk
        legend = tk.Frame(self.root, bg="#25252b")
        legend.pack(side=tk.BOTTOM, fill=tk.X)
        entries = [
            ("start", "#4caf50"),
            ("end", "#ef5350"),
            ("restricted (2 turns, dashed)", "#ff9800"),
            ("priority (preferred)", "#ffd54f"),
            ("blocked", "#8a8a8a"),
            ("active link this turn", "#42a5f5"),
        ]
        for text, color in entries:
            tk.Label(
                legend, text="\u25cf " + text, fg=color, bg="#25252b",
                font=("Helvetica", 9),
            ).pack(side=tk.LEFT, padx=8, pady=4)

    # -- Playback controls ------------------------------------------------

    def _toggle_play(self) -> None:
        self.playing = not self.playing
        self.play_button.config(
            text="\u23f8 Pause" if self.playing else "\u25b6 Play"
        )
        if self.playing:
            self._tick()

    def _tick(self) -> None:
        if not self.playing:
            return
        if self.current_turn >= self.result.total_turns:
            self._toggle_play()
            return
        self.current_turn += 1
        self._sync_scale()
        self._render_frame()
        self.root.after(self.frame_delay_ms, self._tick)

    def _step_forward(self) -> None:
        self._pause()
        self.current_turn = min(
            self.current_turn + 1, max(1, self.result.total_turns)
        )
        self._sync_scale()
        self._render_frame()

    def _step_back(self) -> None:
        self._pause()
        self.current_turn = max(self.current_turn - 1, 1)
        self._sync_scale()
        self._render_frame()

    def _on_scale(self, raw_value: str) -> None:
        self._pause()
        self.current_turn = int(float(raw_value))
        self._render_frame()

    def _pause(self) -> None:
        if self.playing:
            self.playing = False
            self.play_button.config(text="\u25b6 Play")

    def _sync_scale(self) -> None:
        self.turn_scale.set(self.current_turn)

    # -- Layout ------------------------------------------------------------

    def _layout(self) -> Tuple[Dict[str, Tuple[float, float]], float]:
        """Project every zone into current canvas pixel coordinates.

        Positions are rescaled on every call using the canvas's live
        width/height, and the node radius shrinks automatically when
        zones are packed closely together, so nothing overlaps.
        """
        width = max(self.canvas.winfo_width(), 100)
        height = max(self.canvas.winfo_height(), 100)
        zones = self.network.zones

        xs = [z.x for z in zones.values()]
        ys = [z.y for z in zones.values()]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        span_x = (max_x - min_x) or 1
        span_y = (max_y - min_y) or 1
        inner_w = max(width - 2 * self._MARGIN_X, 40)
        inner_h = max(height - 2 * self._MARGIN_Y, 40)

        coords: Dict[str, Tuple[float, float]] = {}
        for name, zone in zones.items():
            norm_x = (zone.x - min_x) / span_x
            norm_y = (zone.y - min_y) / span_y
            cx = self._MARGIN_X + norm_x * inner_w
            # Flip Y so a larger map-file Y coordinate appears higher
            # on screen, matching how the map was likely drawn.
            cy = self._MARGIN_Y + (1 - norm_y) * inner_h
            coords[name] = (cx, cy)

        radius = self._MAX_RADIUS
        points = list(coords.values())
        for i, (x1, y1) in enumerate(points):
            for x2, y2 in points[i + 1:]:
                dist = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
                if dist > 0:
                    radius = min(radius, dist / 2.6)
        radius = max(self._MIN_RADIUS, min(self._MAX_RADIUS, radius))
        return coords, radius

    # -- Simulation state lookups ------------------------------------------

    def _drones_by_zone(self, turn: int) -> Dict[str, List[str]]:
        occupants: Dict[str, List[str]] = {}
        for drone in self.result.drones:
            last_zone: Optional[str] = None
            for step in drone.plan:
                if step.zone_hold is not None and step.turn <= turn:
                    last_zone = step.zone_hold
                if step.turn > turn:
                    break
            if last_zone is not None:
                occupants.setdefault(last_zone, []).append(
                    f"D{drone.drone_id}"
                )
        return occupants

    def _active_links(self, turn: int) -> set[Tuple[str, str]]:
        links: set[Tuple[str, str]] = set()
        for drone in self.result.drones:
            for step in drone.plan:
                if step.turn == turn and step.link_hold is not None:
                    links.add(pair_key(*step.link_hold))
        return links

    def _safe_fill(self, color: Optional[str], fallback: str) -> str:
        """Resolve a map-file color name to a Tk-safe color string."""
        if not color:
            return fallback
        if color not in self._safe_colors:
            try:
                self.canvas.winfo_rgb(color)
                self._safe_colors[color] = color
            except self._tk.TclError:
                self._safe_colors[color] = fallback
        return self._safe_colors[color]

    # -- Drawing -------------------------------------------------------

    def _render_frame(self) -> None:
        self.canvas.delete("all")
        coords, radius = self._layout()
        self.turn_label.config(
            text=f"Turn {self.current_turn} / {self.result.total_turns}"
        )
        self._sync_scale()

        self._draw_links(coords)
        self._draw_zones(coords, radius)

        if self.current_turn >= self.result.total_turns:
            self.canvas.create_text(
                self.canvas.winfo_width() / 2, 18,
                text="All drones delivered",
                fill="#66bb6a", font=("Helvetica", 11, "bold"),
            )

    def _draw_links(
        self, coords: Dict[str, Tuple[float, float]]
    ) -> None:
        active = self._active_links(self.current_turn)
        for conn in self.network.connections:
            if conn.zone_a not in coords or conn.zone_b not in coords:
                continue
            x1, y1 = coords[conn.zone_a]
            x2, y2 = coords[conn.zone_b]
            zone_a = self.network.zones[conn.zone_a]
            zone_b = self.network.zones[conn.zone_b]
            is_restricted = (
                zone_a.zone_type is ZoneType.RESTRICTED
                or zone_b.zone_type is ZoneType.RESTRICTED
            )
            is_active = pair_key(conn.zone_a, conn.zone_b) in active
            color = "#42a5f5" if is_active else (
                "#ff9800" if is_restricted else "#4a4a52"
            )
            width = 3.0 if is_active else 1.6
            if is_restricted:
                self.canvas.create_line(
                    x1, y1, x2, y2, fill=color, width=width, dash=(6, 4)
                )
            else:
                self.canvas.create_line(
                    x1, y1, x2, y2, fill=color, width=width
                )

    def _draw_zones(
        self,
        coords: Dict[str, Tuple[float, float]],
        radius: float,
    ) -> None:
        occupants = self._drones_by_zone(self.current_turn)
        font_size = max(8, int(radius * 0.45))
        for name, zone in self.network.zones.items():
            cx, cy = coords[name]
            fill = self._safe_fill(zone.color, "#3d3d44")
            outline, outline_width = self._zone_style(zone)

            self.canvas.create_oval(
                cx - radius, cy - radius, cx + radius, cy + radius,
                fill=fill, outline=outline, width=outline_width,
            )
            self.canvas.create_text(
                cx, cy - radius - 12, text=name, fill="#f0f0f0",
                font=("Helvetica", font_size, "bold"),
            )

            here = occupants.get(name)
            if here:
                text = (
                    ",".join(here) if len(here) <= 3
                    else ",".join(here[:3]) + f"+{len(here) - 3}"
                )
                self.canvas.create_text(
                    cx, cy, text=text, fill="#101012",
                    font=("Helvetica", font_size, "bold"),
                )

    def _zone_style(self, zone: Zone) -> Tuple[str, int]:
        """Outline color/width encoding this zone's role and type."""
        if zone.is_start:
            return "#4caf50", 4
        if zone.is_end:
            return "#ef5350", 4
        if zone.zone_type is ZoneType.RESTRICTED:
            return "#ff9800", 3
        if zone.zone_type is ZoneType.PRIORITY:
            return "#ffd54f", 3
        if zone.zone_type is ZoneType.BLOCKED:
            return "#8a8a8a", 2
        return "#c9c9d1", 2


# ---------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------


def build_arg_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="drone_system.py",
        description="Fly-In: multi-drone routing simulation.",
    )
    parser.add_argument("map_file", help="Path to the map description "
                        "file to simulate.")
    parser.add_argument(
        "--gui", action="store_true",
        help="Also open a graphical, animated view (requires Tk).",
    )
    parser.add_argument(
        "--no-color", action="store_true",
        help="Disable ANSI colors in the terminal output.",
    )
    parser.add_argument(
        "--summary", action="store_true",
        help="Print secondary performance metrics after the run.",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Run the CLI. Returns the process exit code."""
    args = build_arg_parser().parse_args(argv)

    try:
        nb_drones, network = MapParser.parse(args.map_file)
        engine = SimulationEngine(nb_drones, network)
        result = engine.plan()
    except MapParseError as exc:
        print(f"Parsing error: {exc}", file=sys.stderr)
        return 1
    except RuntimeError as exc:
        print(f"Simulation error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001 - top level safety net
        print(f"Unexpected error: {exc}", file=sys.stderr)
        return 1

    visualizer = Visualizer(enabled=not args.no_color)
    for line in engine.render_text(result, visualizer):
        print(line)
    if args.summary:
        for line in engine.render_summary(result):
            print(line)

    if args.gui:
        try:
            gui = GuiEngine(network, result)
        except ImportError:
            print(
                "GUI requested but tkinter is not available on this "
                "system; continuing with text output only.",
                file=sys.stderr,
            )
        else:
            try:
                gui.run()
            except Exception as exc:  # noqa: BLE001 - Tk runtime issues
                print(
                    f"GUI could not be started ({exc}); the text "
                    "output above is still valid.",
                    file=sys.stderr,
                )
    return 0


if __name__ == "__main__":
    sys.exit(main())
