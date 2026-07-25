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

    def function(self):
        pass