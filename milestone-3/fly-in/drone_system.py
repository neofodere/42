#!/usr/bin/env python3
"""Drone Routing and Simulation System.

This module implements an optimized, spatiotemporal drone routing engine
adhering to strict capacity, connection, and scheduling constraints.
"""

import heapq
import itertools
import re
import sys
import tkinter as tk
import time
from typing import Dict, List, Optional, Set, Tuple


class Zone:
    """Represents a network zone (hub) with specific constraints."""

    def __init__(
        self,
        name: str,
        x: int,
        y: int,
        zone_type: str = "normal",
        color: str = "none",
        max_drones: int = 1,
    ) -> None:
        """Initialize a Zone object."""
        self.name: str = name
        self.x: int = x
        self.y: int = y
        self.zone_type: str = zone_type
        self.color: str = color
        self.max_drones: int = max_drones


class Connection:
    """Represents a bidirectional link between two zones."""

    def __init__(self, zone1: str, zone2: str, max_link_capacity: int = 1) -> None:
        """Initialize a Connection object."""
        self.zone1: str = zone1
        self.zone2: str = zone2
        self.max_link_capacity: int = max_link_capacity


class DroneNetwork:
    """Manages the graph structure of zones and connections."""

    def __init__(self) -> None:
        """Initialize the Drone Network."""
        self.zones: Dict[str, Zone] = {}
        self.connections: List[Connection] = []
        self.adj: Dict[str, List[str]] = {}
        self.start_hub: Optional[str] = None
        self.end_hub: Optional[str] = None

    def add_zone(self, zone: Zone, is_start: bool = False, is_end: bool = False) -> None:
        """Add a zone to the network layout."""
        self.zones[zone.name] = zone
        self.adj[zone.name] = []
        if is_start:
            self.start_hub = zone.name
        if is_end:
            self.end_hub = zone.name

    def add_connection(self, conn: Connection) -> None:
        """Add a bidirectional link between two valid zones."""
        self.connections.append(conn)
        self.adj[conn.zone1].append(conn.zone2)
        self.adj[conn.zone2].append(conn.zone1)

    def get_link_capacity(self, u: str, v: str) -> int:
        """Retrieve the maximum link traversal capacity between two zones."""
        for conn in self.connections:
            if (conn.zone1 == u and conn.zone2 == v) or (
                conn.zone1 == v and conn.zone2 == u
            ):
                return conn.max_link_capacity
        return 1


class Parser:
    """Parses and validates the input map file configuration."""

    @staticmethod
    def parse_file(filepath: str) -> Tuple[int, DroneNetwork]:
        """Parse the input configuration file completely."""
        network = DroneNetwork()
        nb_drones = 0
        seen_connections: Set[Tuple[str, str]] = set()

        with open(filepath, "r", encoding="utf-8") as file:
            for line_idx, raw_line in enumerate(file, 1):
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue

                if line.startswith("nb_drones:"):
                    match = re.match(r"nb_drones:\s*(\d+)", line)
                    if not match:
                        raise ValueError(f"Line {line_idx}: Invalid drone count.")
                    nb_drones = int(match.group(1))
                    if nb_drones <= 0:
                        raise ValueError(f"Line {line_idx}: Drone count <= 0.")
                    continue

                if (
                    line.startswith("start_hub:")
                    or line.startswith("end_hub:")
                    or line.startswith("hub:")
                ):
                    Parser._parse_zone_line(line, line_idx, network)
                    continue

                if line.startswith("connection:"):
                    Parser._parse_connection_line(
                        line, line_idx, network, seen_connections
                    )
                    continue

                raise ValueError(f"Line {line_idx}: Unknown syntax instruction.")

        if not network.start_hub or not network.end_hub:
            raise ValueError("Parser Error: Missing unique start or end hub.")

        return nb_drones, network

    @staticmethod
    def _parse_zone_line(line: str, idx: int, network: DroneNetwork) -> None:
        prefix_match = re.match(r"^(start_hub|end_hub|hub):\s*", line)
        if not prefix_match:
            raise ValueError(f"Line {idx}: Invalid zone prefix definition.")

        prefix = prefix_match.group(1)
        rem = line[prefix_match.end() :].strip()

        meta_match = re.search(r"\[(.*?)\]", rem)
        meta_str = meta_match.group(1) if meta_match else ""
        if meta_match:
            rem = rem[: meta_match.start()].strip()

        tokens = rem.split()
        if len(tokens) < 3:
            raise ValueError(f"Line {idx}: Missing zone name or coordinates.")

        name, x_str, y_str = tokens[0], tokens[1], tokens[2]
        if "-" in name or " " in name:
            raise ValueError(f"Line {idx}: Zone name contains invalid symbols.")

        try:
            x, y = int(x_str), int(y_str)
        except ValueError:
            raise ValueError(f"Line {idx}: Coordinates must be integer types.")

        z_type, color, max_d = "normal", "none", 1
        if meta_str:
            for meta_item in meta_str.split():
                if "=" in meta_item:
                    k, v = meta_item.split("=", 1)
                    if k == "zone":
                        z_type = v
                    elif k == "color":
                        color = v
                    elif k == "max_drones":
                        max_d = int(v)

        if z_type not in ["normal", "blocked", "restricted", "priority"]:
            raise ValueError(f"Line {idx}: Unknown zone type '{z_type}'.")
        if max_d <= 0:
            raise ValueError(f"Line {idx}: Capacity must be positive.")

        zone = Zone(name, x, y, z_type, color, max_d)
        network.add_zone(zone, prefix == "start_hub", prefix == "end_hub")

    @staticmethod
    def _parse_connection_line(
        line: str, idx: int, network: DroneNetwork, seen: Set[Tuple[str, str]]
    ) -> None:
        rem = line[len("connection:") :].strip()
        meta_match = re.search(r"\[(.*?)\]", rem)
        meta_str = meta_match.group(1) if meta_match else ""
        if meta_match:
            rem = rem[: meta_match.start()].strip()

        link_match = re.match(r"^([^\s-]+)-([^\s-]+)$", rem)
        if not link_match:
            raise ValueError(f"Line {idx}: Invalid connection syntax.")

        u, v = link_match.group(1), link_match.group(2)
        if u not in network.zones or v not in network.zones:
            raise ValueError(f"Line {idx}: Undefined nodes referenced.")

        norm_link = (u, v) if u < v else (v, u)
        if norm_link in seen:
            raise ValueError(f"Line {idx}: Duplicate connection detected.")
        seen.add(norm_link)

        max_cap = 1
        if meta_str:
            for item in meta_str.split():
                if "=" in item:
                    k, val = item.split("=", 1)
                    if k == "max_link_capacity":
                        max_cap = int(val)

        if max_cap <= 0:
            raise ValueError(f"Line {idx}: Link capacity must be positive.")

        network.add_connection(Connection(u, v, max_cap))


class ReservationTable:
    """Manages spatiotemporal grid resource lock allocation states."""

    def __init__(self, network: DroneNetwork) -> None:
        """Initialize the reservation structures."""
        self.network: DroneNetwork = network
        self.zone_booking: Dict[str, Dict[int, int]] = {}
        self.link_booking: Dict[Tuple[str, str], Dict[int, int]] = {}

    def is_zone_free(self, zone_name: str, time: int) -> bool:
        """Check if a zone has available capacity at a specific time turn."""
        if zone_name == self.network.start_hub or zone_name == self.network.end_hub:
            return True
        zone = self.network.zones[zone_name]
        if zone.zone_type == "blocked":
            return False
        booked = self.zone_booking.get(zone_name, {}).get(time, 0)
        return booked < zone.max_drones

    def is_link_free(self, u: str, v: str, time: int) -> bool:
        """Check if a connection has link traversal capacity available."""
        link_key = (u, v) if u < v else (v, u)
        max_cap = self.network.get_link_capacity(u, v)
        booked = self.link_booking.get(link_key, {}).get(time, 0)
        return booked < max_cap

    def reserve_path(self, path: List[Tuple[str, int, str]]) -> None:
        """Commit a planned spatiotemporal path layout allocation."""
        for i in range(len(path) - 1):
            curr_zone, curr_t, status = path[i]
            next_zone, next_t, _ = path[i + 1]

            if curr_zone == next_zone:
                if curr_zone != self.network.start_hub:
                    self.zone_booking.setdefault(curr_zone, {}).setdefault(curr_t + 1, 0)
                    self.zone_booking[curr_zone][curr_t + 1] += 1
            else:
                link_key = (curr_zone, next_zone) if curr_zone < next_zone else (next_zone, curr_zone)
                self.link_booking.setdefault(link_key, {}).setdefault(curr_t, 0)
                self.link_booking[link_key][curr_t] += 1

                if status == "transit":
                    self.link_booking.setdefault(link_key, {}).setdefault(curr_t + 1, 0)
                    self.link_booking[link_key][curr_t + 1] += 1

                if next_zone != self.network.end_hub:
                    self.zone_booking.setdefault(next_zone, {}).setdefault(next_t, 0)
                    self.zone_booking[next_zone][next_t] += 1


class PathFinder:
    """Computes optimal collision-free spatiotemporal drone trajectories."""

    def __init__(self, network: DroneNetwork) -> None:
        """Initialize the trajectory pathfinder instance."""
        self.network: DroneNetwork = network
        self.heuristic_cache: Dict[str, float] = {}
        self._compute_static_heuristics()
        self.tie_breaker = itertools.count()

    def _compute_static_heuristics(self) -> None:
        end = self.network.end_hub
        if not end:
            return
        queue: List[Tuple[float, str]] = [(0.0, end)]
        self.heuristic_cache[end] = 0.0

        while queue:
            dist, u = heapq.heappop(queue)
            if dist > self.heuristic_cache.get(u, float("inf")):
                continue
            for v in self.network.adj[u]:
                v_zone = self.network.zones[v]
                if v_zone.zone_type == "blocked":
                    continue
                cost = 1.0
                if v_zone.zone_type == "restricted":
                    cost = 2.0
                elif v_zone.zone_type == "priority":
                    cost = 0.5

                if dist + cost < self.heuristic_cache.get(v, float("inf")):
                    self.heuristic_cache[v] = dist + cost
                    heapq.heappush(queue, (dist + cost, v))

    def search(
        self, start_t: int, table: ReservationTable
    ) -> Optional[List[Tuple[str, int, str]]]:
        """Calculate the shortest spatiotemporal path using A*."""
        start = self.network.start_hub
        end = self.network.end_hub
        if not start or not end:
            return None

        h_start = self.heuristic_cache.get(start, 0.0)
        open_set: List[Tuple[float, float, int, str, int, list]] = [
            (h_start, 0.0, next(self.tie_breaker), start, start_t, [(start, start_t, "arrived")])
        ]
        visited: Set[Tuple[str, int]] = set()

        max_horizon = start_t + 1000

        while open_set:
            _, g, _, u, t, history = heapq.heappop(open_set)

            if u == end:
                return history

            if (u, t) in visited or t > max_horizon:
                continue
            visited.add((u, t))

            if u == start or table.is_zone_free(u, t + 1):
                next_history = history + [(u, t + 1, "arrived")]
                h_val = self.heuristic_cache.get(u, 0.0)
                heapq.heappush(
                    open_set,
                    (g + 1 + h_val, g + 1, next(self.tie_breaker), u, t + 1, next_history),
                )

            for v in self.network.adj[u]:
                v_zone = self.network.zones[v]
                if v_zone.zone_type == "blocked":
                    continue

                if not table.is_link_free(u, v, t):
                    continue

                if v_zone.zone_type == "restricted":
                    if table.is_link_free(u, v, t + 1) and table.is_zone_free(v, t + 2):
                        next_hist = history + [(v, t + 1, "transit"), (v, t + 2, "arrived")]
                        h_val = self.heuristic_cache.get(v, 0.0)
                        heapq.heappush(
                            open_set,
                            (g + 2 + h_val, g + 2, next(self.tie_breaker), v, t + 2, next_hist),
                        )
                else:
                    if table.is_zone_free(v, t + 1):
                        next_hist = history + [(v, t + 1, "arrived")]
                        h_val = self.heuristic_cache.get(v, 0.0)
                        cost_step = 0.5 if v_zone.zone_type == "priority" else 1.0
                        heapq.heappush(
                            open_set,
                            (g + cost_step + h_val, g + cost_step, next(self.tie_breaker), v, t + 1, next_hist),
                        )
        return None


class Visualizer:
    """Handles terminal color translation configurations."""

    def __init__(self) -> None:
        self.ansi_palette: Dict[str, str] = {
            "red": "\033[91m",
            "green": "\033[92m",
            "yellow": "\033[93m",
            "blue": "\033[94m",
            "magenta": "\033[95m",
            "cyan": "\033[96m",
            "gray": "\033[90m",
            "none": "\033[0m",
        }
        self.reset: str = "\033[0m"

    def colorize(self, text: str, color_name: str) -> str:
        color_code = self.ansi_palette.get(color_name.lower(), self.reset)
        return f"{color_code}{text}{self.reset}"


class GuiEngine:
    """Optional GUI window renderer to fulfill advanced visual instructions."""

    def __init__(self, network: DroneNetwork, schedules: Dict[int, List[Tuple[str, int, str]]], max_turn: int) -> None:
        self.network = network
        self.schedules = schedules
        self.max_turn = max_turn
        self.current_turn = 1

        self.root = tk.Tk()
        self.root.title("Fly-In: Drone Routing GUI Monitor")
        self.canvas = tk.Canvas(self.root, width=900, height=600, bg="#222222")
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.label = tk.Label(self.root, text="Turn: 1", font=("Helvetica", 16, "bold"), fg="white", bg="#333333")
        self.label.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.node_radius = 25
        self._render_loop()

    def _render_loop(self) -> None:
        if self.current_turn > self.max_turn:
            self.label.config(text=f"Simulation Finished! Total turns: {self.max_turn}")
            self.root.mainloop()
            return

        self.canvas.delete("all")
        self.label.config(text=f"Simulation Step Turn: {self.current_turn} / {self.max_turn}")

        # Map bounds normalization to dynamically scale maps onto the canvas
        xs = [z.x for z in self.network.zones.values()]
        ys = [z.y for z in self.network.zones.values()]
        min_x, max_x = (min(xs), max(xs)) if xs else (0, 10)
        min_y, max_y = (min(ys), max(ys)) if ys else (0, 10)
        
        span_x = (max_x - min_x) if max_x != min_x else 1
        span_y = (max_y - min_y) if max_y != min_y else 1

        def get_coords(name: str) -> Tuple[float, float]:
            z = self.network.zones[name]
            cx = 80 + ((z.x - min_x) / span_x) * 740
            cy = 80 + ((z.y - min_y) / span_y) * 440
            return cx, cy

        # Draw Connections
        for conn in self.network.connections:
            x1, y1 = get_coords(conn.zone1)
            x2, y2 = get_coords(conn.zone2)
            self.canvas.create_line(x1, y1, x2, y2, fill="#555555", width=2)

        # Build location contents for current turn
        drone_positions: Dict[str, List[str]] = {}
        for d_id, path in self.schedules.items():
            for node, t, status in path:
                if t == self.current_turn:
                    drone_positions.setdefault(node, []).append(f"D{d_id}")

        # Draw Zones
        for name, zone in self.network.zones.items():
            cx, cy = get_coords(name)
            bg_color = zone.color if zone.color in ["red", "green", "blue", "yellow", "magenta", "cyan", "gray"] else "#444444"
            if name == self.network.start_hub:
                bg_color = "green"
            elif name == self.network.end_hub:
                bg_color = "red"

            self.canvas.create_oval(cx - self.node_radius, cy - self.node_radius, cx + self.node_radius, cy + self.node_radius, fill=bg_color, outline="white", width=2)
            self.canvas.create_text(cx, cy - 35, text=name, fill="white", font=("Arial", 10, "bold"))
            
            # Draw drones inside/near the zone node
            occupants = drone_positions.get(name, [])
            if occupants:
                occ_text = ", ".join(occupants)
                self.canvas.create_text(cx, cy, text=occ_text, fill="black", font=("Arial", 9, "bold"))

        self.current_turn += 1
        self.root.after(800, self._render_loop)


class SimulationEngine:
    """Coordinates simulation scheduling, execution loops, and reporting."""

    def __init__(self, nb_drones: int, network: DroneNetwork) -> None:
        self.nb_drones: int = nb_drones
        self.network: DroneNetwork = network
        self.table: ReservationTable = ReservationTable(network)
        self.pathfinder: PathFinder = PathFinder(network)
        self.visualizer: Visualizer = Visualizer()

    def run(self, launch_gui: bool = False) -> None:
        drone_schedules: Dict[int, List[Tuple[str, int, str]]] = {}

        for drone_id in range(1, self.nb_drones + 1):
            allocated = False
            for start_time in range(0, 500):
                path = self.pathfinder.search(start_time, self.table)
                if path:
                    self.table.reserve_path(path)
                    drone_schedules[drone_id] = path
                    allocated = True
                    break
            if not allocated:
                print(f"Error: Could not allocate route layout for Drone D{drone_id}.")
                sys.exit(1)

        max_turn = 0
        for path in drone_schedules.values():
            if path:
                max_turn = max(max_turn, path[-1][1])

        # Terminal text stdout simulation loop
        for t in range(1, max_turn + 1):
            turn_actions: List[str] = []
            for drone_id in range(1, self.nb_drones + 1):
                path = drone_schedules[drone_id]

                state_at_t = None
                prev_state = None
                for node, time_val, status in path:
                    if time_val == t:
                        state_at_t = (node, status)
                        break
                    if time_val < t:
                        prev_state = (node, status)

                if state_at_t:
                    node, status = state_at_t
                    if status == "transit":
                        if prev_state:
                            p_node, _ = prev_state
                            conn_str = f"{p_node}-{node}"
                            colored_move = self.visualizer.colorize(
                                f"D{drone_id}-{conn_str}",
                                self.network.zones[node].color,
                            )
                            turn_actions.append(colored_move)
                    else:
                        if prev_state and prev_state[0] == node:
                            continue
                        colored_move = self.visualizer.colorize(
                            f"D{drone_id}-{node}",
                            self.network.zones[node].color,
                        )
                        turn_actions.append(colored_move)

            if turn_actions:
                print(" ".join(turn_actions))

        if launch_gui:
            gui = GuiEngine(self.network, drone_schedules, max_turn)
            gui.root.mainloop()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 drone_system.py <map_file> [--gui]")
        sys.exit(1)

    gui_flag = "--gui" in sys.argv
    map_path = sys.argv[1] if sys.argv[1] != "--gui" else sys.argv[2]

    try:
        drones_count, drone_network = Parser.parse_file(map_path)
        engine = SimulationEngine(drones_count, drone_network)
        engine.run(launch_gui=gui_flag)
    except Exception as err:
        print(f"Execution Stopped: {err}", file=sys.stderr)
        sys.exit(1)