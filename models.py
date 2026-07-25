from enum import Enum
from dataclasses import  dataclass, field
from typing import List

class ZoneType(Enum):
    NORMAL = "normal"
    RESTRICTED = "restricted"
    PRIORITY = "priority"
    BLOCKED = "blocked"

class ConfigFileError(Exception):
    def __init__(self, message):
        super().__init__(message)


@dataclass
class Connection:
    HubA: str
    HubB: str
    max_link_capacity: int


@dataclass
class HubMetadata:
    zone: ZoneType = ZoneType.NORMAL
    color: str | None = None
    max_drones: int = 1

@dataclass
class Hub:
    name: str
    x: int
    y: int
    is_start: bool
    is_end: bool
    metadata: HubMetadata = field(default_factory=HubMetadata)


class Graph:
    def __init__(
        self,
        nb_drones: int ,
        start_hub: Hub,
        end_hub: Hub,
        hubs: list[Hub],
        connections: List[Connection]
    ) -> None:
        self.nb_drones: int = nb_drones
        self.start_hub: Hub = start_hub
        self.end_hub: Hub = end_hub
        self.hubs: list[Hub] = hubs
        self.connections: List[Connection] = connections
        self.zones = {hub.name: hub for hub in hubs}

    def get_zone_by_name(self, zone_name):
        return self.zones[zone_name]

    def path_of_zone_obj (self, path: list[tuple[str, int]]) -> list[tuple[Hub, int]]:
        return [
            (self.get_zone_by_name(zone_name), turn)
            for zone_name, turn in path
        ]

    def get_neighbors(self, hub: Hub):
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

    def get_connection(self, hub_a, hub_b):
        for conn in self.connections:
            conn_hub_a = self.get_zone_by_name(conn.HubA)
            conn_hub_b = self.get_zone_by_name(conn.HubB)
            if (conn_hub_a == hub_a and conn_hub_b == hub_b) or \
               (conn_hub_a == hub_b and conn_hub_b == hub_a):
                return conn
        return None