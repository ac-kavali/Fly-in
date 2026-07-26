"""Pathfinding utilities for routing drones through the graph.

Provides a reservation table to track zone/connection usage across
turns, and a Dijkstra-based pathfinder that respects those
reservations, zone capacities, and connection capacities.
"""

import heapq

from models import Hub
from models import Graph, ZoneType


class ReservationTable:
    """Tracks reserved zones and connections during pathfinding.

    Reservations prevent drones from occupying the same zone or
    using the same connection beyond its capacity at a given turn.
    """

    def __init__(self, graph: Graph) -> None:
        """Initialize an empty reservation table.

        Args:
            graph: Graph containing all zones and connections.

        Returns:
            None
        """
        self.graph = graph
        self.zone_table: dict[tuple[str, int], int] = {}
        self.connection_table: dict[tuple[str, str, int], int] = {}

    def can_enter_zone(self, zone: Hub, turn: int) -> bool:
        """Check whether a drone may enter a zone at a given turn.

        Start and end zones have unlimited capacity.

        Args:
            zone: Zone to check.
            turn: Simulation turn.

        Returns:
            bool: True if the zone has available capacity, otherwise
            False.
        """
        if zone.is_start or zone.is_end:
            return True
        result = self.zone_table.get((zone.name, turn), 0)
        return result < zone.metadata.max_drones

    def reserve(self, zone: str, turn: int) -> None:
        """Reserve a zone for a specific turn.

        Args:
            zone: Name of the zone to reserve.
            turn: Simulation turn.

        Returns:
            None
        """
        key = (zone, turn)
        self.zone_table[key] = (self.zone_table.get(key, 0) + 1)

    def can_use_connection(
        self,
        c_zone: Hub,
        n_zone: Hub,
        turn: int,
        capacity: int
    ) -> bool:
        """Check whether a connection may be used at a given turn.

        Args:
            c_zone: Current zone.
            n_zone: Destination zone.
            turn: Simulation turn.
            capacity: Maximum connection capacity.

        Returns:
            bool: True if the connection has available capacity,
            otherwise False.
        """
        key = self._connection_key(c_zone, n_zone, turn)
        used = self.connection_table.get(key, 0)
        return used < capacity

    def reserve_connection(
        self,
        c_zone: str,
        n_zone: str,
        turn: int
    ) -> None:
        """Reserve a connection for a specific turn.

        Args:
            c_zone: Name of the starting zone.
            n_zone: Name of the destination zone.
            turn: Simulation turn.

        Returns:
            None
        """
        obj_c_zone = self.graph.get_zone_by_name(c_zone)
        obj_n_zone = self.graph.get_zone_by_name(n_zone)
        if obj_c_zone is None or obj_n_zone is None:
            return
        key = self._connection_key(obj_c_zone, obj_n_zone, turn)
        self.connection_table[key] = (self.connection_table.get(key, 0) + 1)

    def _connection_key(
        self,
        c_zone: Hub,
        n_zone: Hub,
        turn: int
    ) -> tuple[str, str, int]:
        """Build a unique key for a connection reservation.

        The order of the zones does not matter because connections
        are undirected.

        Args:
            c_zone: First connected zone.
            n_zone: Second connected zone.
            turn: Simulation turn.

        Returns:
            tuple[str, str, int]: A tuple identifying the connection
            and turn.
        """
        a = min(c_zone.name, n_zone.name)
        b = max(c_zone.name, n_zone.name)
        return a, b, turn


class Pathfinder:
    """Finds paths for drones while respecting reservation rules.

    Uses a Dijkstra-based search with reservations to avoid
    conflicts between drones.
    """

    def find_path(
        self,
        graph: Graph,
        start: Hub,
        end: Hub,
        nb_drones: int,
        reservations: ReservationTable,
    ) -> list[tuple[str, int]]:
        """Find a valid path from the start zone to the end zone.

        The search respects zone capacities, connection capacities,
        restricted zones, and existing reservations.

        Args:
            graph: Graph containing all zones and connections.
            start: Starting zone.
            end: Destination zone.
            nb_drones: Total number of drones in the simulation.
            reservations: Reservation table used to avoid conflicts.

        Returns:
            list[tuple[str, int]]: A list of (zone_name, turn) pairs
            describing the path. Returns an empty list if no valid
            path is found.
        """
        heap: list[tuple[int, int, str, list[tuple[str, int]]]] = []
        path: list[tuple[str, int]] = []
        start_zone = start.name
        heapq.heappush(heap, (0, 0, start_zone, path))
        max_time = len(graph.zones) * nb_drones * 2
        visited: set[tuple[str, int]] = set()

        while heap:
            current_turn, _, current_zone, path = heapq.heappop(heap)
            if current_turn >= max_time:
                continue
            ob_current_hub = graph.get_zone_by_name(current_zone)
            if ob_current_hub is None:
                continue
            state = (current_zone, current_turn)
            if state in visited:
                continue
            new_path = path + [state]
            if current_zone == end.name:
                return new_path
            visited.add(state)
            print(f"this is visited: {visited}")

            wait_turn = current_turn + 1

            if (
                    wait_turn <= max_time
                    and reservations.can_enter_zone(ob_current_hub, wait_turn)
            ):
                priority = 0 if (
                        ob_current_hub.metadata.zone == ZoneType.PRIORITY
                ) else 1
                heapq.heappush(heap, (wait_turn, priority,
                                      current_zone, new_path))

            for neighbor in graph.get_neighbors(ob_current_hub):
                neighbor_req_turns = graph.get_movement_cost(neighbor)
                # get_neighbors() already excludes BLOCKED zones, so
                # this is never None in practice; the check exists to
                # satisfy static typing (get_movement_cost declares
                # int | None) without altering runtime behavior.
                if neighbor_req_turns is None:
                    continue
                new_turn = current_turn + neighbor_req_turns
                neighbor_state = (neighbor.name, new_turn)
                if neighbor_state in visited:
                    continue
                connection = graph.get_connection(ob_current_hub, neighbor)
                if connection is None:
                    continue

                if not reservations.can_enter_zone(neighbor, new_turn):
                    continue
                connection_ok = True

                start_turn = current_turn + 1
                end_turn = current_turn + neighbor_req_turns
                for t in range(start_turn, end_turn + 1):
                    if not reservations.can_use_connection(
                        ob_current_hub,
                        neighbor,
                        t,
                        connection.max_link_capacity
                    ):
                        connection_ok = False
                        break

                if not connection_ok:
                    continue
                priority = (
                    0 if neighbor.metadata.zone == ZoneType.PRIORITY else 1
                )

                heapq.heappush(
                    heap,
                    (new_turn, priority, neighbor.name, new_path))
        return []
