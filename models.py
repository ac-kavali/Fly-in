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


@dataclass
class Graph:
    nb_drones: int
    start_hub: Hub
    end_hub: Hub | None
    hubs: list[Hub] | None
    connections: List[Connection] | None