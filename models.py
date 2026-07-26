"""Domain models for the drone routing graph.

Defines the zone types, hub metadata, connections between hubs, and
the `Graph` container used by the pathfinding and parsing modules.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List


class ZoneType(Enum):
    """Enumeration of the possible zone types a hub can have."""

    NORMAL = "normal"
    RESTRICTED = "restricted"
    PRIORITY = "priority"
    BLOCKED = "blocked"


class ConfigFileError(Exception):
    """Raised when the configuration/map file is invalid or malformed."""

    def __init__(self, message: str) -> None:
        """Initialize the exception with an explanatory message.

        Args:
            message: A human-readable description of the error.

        Returns:
            None
        """
        super().__init__(message)


@dataclass
class Connection:
    """A link between two hubs.

    Attributes:
        HubA: Name of the first hub in the connection.
        HubB: Name of the second hub in the connection.
        max_link_capacity: Maximum number of drones the link can
            carry at once.
    """

    HubA: str
    HubB: str
    max_link_capacity: int


@dataclass
class HubMetadata:
    """Metadata describing a hub's zone, color, and drone capacity.

    Attributes:
        zone: The type of zone the hub belongs to.
        color: Optional display color for the hub.
        max_drones: Maximum number of drones the hub can hold at once.
    """

    zone: ZoneType = ZoneType.NORMAL
    color: str | None = None
    max_drones: int = 1


@dataclass
class Hub:
    """A single hub (node) in the routing graph.

    Attributes:
        name: The unique name of the hub.
        x: The x-coordinate of the hub.
        y: The y-coordinate of the hub.
        is_start: Whether this hub is the starting point.
        is_end: Whether this hub is the destination.
        metadata: Additional metadata associated with the hub.
    """

    name: str
    x: int
    y: int
    is_start: bool
    is_end: bool
    metadata: HubMetadata = field(default_factory=HubMetadata)


class Graph:
    """Represents the full hub/connection graph used for pathfinding."""

    def __init__(
        self,
        nb_drones: int,
        start_hub: Hub,
        end_hub: Hub,
        hubs: list[Hub],
        connections: List[Connection]

    ) -> None:
        """Initialize the graph with hubs, connections, and drone count.

        Args:
            nb_drones: Number of drones to route through the graph.
            start_hub: The hub where all drones start.
            end_hub: The hub all drones must reach.
            hubs: All hubs present in the graph.
            connections: All connections between hubs in the graph.

        Returns:
            None
        """
        self.nb_drones: int = nb_drones
        self.start_hub: Hub = start_hub
        self.end_hub: Hub = end_hub
        self.hubs: list[Hub] = hubs
        self.connections: List[Connection] = connections
        self.zones = {hub.name: hub for hub in hubs}
        self.zones[start_hub.name] = start_hub
        self.zones[end_hub.name] = end_hub
        self.zone_costs = {
            ZoneType.NORMAL: 1,
            ZoneType.RESTRICTED: 2,
            ZoneType.PRIORITY: 1,
            ZoneType.BLOCKED: None
        }

    def get_zone_by_name(self, zone_name: str) -> Hub:
        """Look up a hub by its name.

        Args:
            zone_name: The name of the hub to retrieve.

        Returns:
            Hub: The hub matching the given name.
        """
        return self.zones[zone_name]

    def path_of_zone_obj(
        self, path: list[tuple[str, int]]
    ) -> list[tuple[Hub, int]]:
        """Convert a path of hub names into a path of hub objects.

        Args:
            path: A sequence of (hub name, turn) pairs.

        Returns:
            list[tuple[Hub, int]]: The corresponding sequence of
            (hub, turn) pairs.
        """
        return [
            (self.get_zone_by_name(zone_name), turn)
            for zone_name, turn in path
        ]

    def get_neighbors(self, hub: Hub) -> list[Hub]:
        """Get all non-blocked hubs directly connected to a hub.

        Args:
            hub: The hub whose neighbors should be found.

        Returns:
            list[Hub]: The neighboring hubs that are not blocked.
        """
        neighbors: list[Hub] = []
        for connection in self.connections:
            HubA_obj = self.get_zone_by_name(connection.HubA)
            HubB_obj = self.get_zone_by_name(connection.HubB)
            if HubA_obj == hub:
                if HubB_obj.metadata.zone != ZoneType.BLOCKED:
                    neighbors.append(HubB_obj)
            elif HubB_obj == hub:
                if HubA_obj.metadata.zone != ZoneType.BLOCKED:
                    neighbors.append(HubA_obj)
        return neighbors

    def get_connection(
        self, hub_a: Hub, hub_b: Hub
    ) -> Connection | None:
        """Find the connection linking two hubs, in either direction.

        Args:
            hub_a: One of the two hubs.
            hub_b: The other hub.

        Returns:
            Connection | None: The matching connection, or None if
            the two hubs are not directly connected.
        """
        for conn in self.connections:
            conn_hub_a = self.get_zone_by_name(conn.HubA)
            conn_hub_b = self.get_zone_by_name(conn.HubB)
            if (conn_hub_a == hub_a and conn_hub_b == hub_b) or \
               (conn_hub_a == hub_b and conn_hub_b == hub_a):
                return conn
        return None

    def get_movement_cost(self, hub: Hub) -> int | None:
        """Get the movement cost for entering a hub's zone type.

        Args:
            hub: The hub whose movement cost should be looked up.

        Returns:
            int | None: The movement cost, or None if the zone is
            blocked.
        """
        return self.zone_costs[hub.metadata.zone]
