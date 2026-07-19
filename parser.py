from dataclasses import dataclass
from enum import Enum
import re
from typing import  List


class Zoneytpes(Enum):
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
    metadata: dict

@dataclass
class Hub:
    name: str
    x: int
    y: int
    is_start: bool
    is_end: bool
    metadata: dict | None = None


@dataclass
class Graph:
    nb_drones: int
    start_hub: Hub
    end_hub: Hub | None
    hubs: list[Hub] | None
    connections: List[Connection] | None


data_checklist = {"start_hub": 0,
                 "end_hub": 0
                  }


class Parser:
    def __init__(self, filename):
        self._filename = filename
        self.meta_data_pattern = re.compile(r"\[(\w+=\S+)(\s+\w+=\S+)*\]")
        self.valid_m_keys = {"zone", "color", "max_drones"}


    @staticmethod
    def _parse_positif_int(string_num: str, data_spec: str, line_number: int):
        absolut_num = string_num[1:] if string_num.startswith("-") else string_num
        if not absolut_num.isdigit():
            raise ConfigFileError(f"Line {line_number}: {data_spec} support only number!")
        elif int(string_num) < 0:
            raise ConfigFileError(f"Line {line_number}: {data_spec} must be a positive number!")
        if "number of drones" in data_spec:
            if int(string_num) == 0:
                raise ConfigFileError(f"Line {line_number}: {data_spec} must be a different to zero!")
        return int(string_num)


    def _parse_hub(self, line, line_number):
        hub = {}
        try:
            hub["name"] = line.split(":")[1].strip().split(" ")[0]
        except IndexError:
            raise ConfigFileError("Messing Hub name")
        if self.meta_data_pattern.match(hub["name"]):
            raise ConfigFileError("Metadata must be after coordinates")

        if hub["name"].isdigit():
            raise ConfigFileError("Hub name can't be number")

        if "-" in hub["name"]:
            raise ConfigFileError("dashes are forbidden in hubs name")

        # Parse x
        try:
            hub["x"] = line.split(":")[1].strip().split(" ")[1]
        except IndexError:
            raise ConfigFileError("Missing x and y")

        hub["x"] = self._parse_positif_int(hub["x"], "x coordinate", line_number)

        # Parse y
        try:
            hub["y"] = line.split(":")[1].strip().split(" ")[2]
        except Exception:
            raise ConfigFileError("Messing y  coordinates")
        if '[' in hub["y"] or hub["y"].isspace():
            raise ConfigFileError("Messing y  coordinates")
        hub["y"] = self._parse_positif_int(hub["y"], "y coordinate", line_number)

        # Parse meta-data
        if len(line.strip().split(" ")) > 4:
            metadata: dict = self._parse_metadata(line, line_number)
            invalid_meta = set(metadata) - self.valid_m_keys
            if invalid_meta:
                raise ConfigFileError(f"Line {line_number}: invalid metadata keys({next(iter(invalid_meta))})")
            hub["metadata"] = metadata
        else:
            hub["metadata"] = None

        return hub


    def _parse_metadata(self, line, line_number):
        metadata_part = " ".join(line.split(" ")[4:]).strip()
        metadata = re.match(self.meta_data_pattern, metadata_part)
        if metadata:
            metadata = re.split(r"[ =]", metadata.group(0))
            metadata = [data.replace("[", "").replace("]", "") for data in metadata]
            total_len = len(metadata[::2])
            metadata = dict(zip(metadata[::2], metadata[1::2]))
            if len(metadata) < total_len:
                raise ConfigFileError(f"Line {line_number}: duplicate meta-data specifications")
            return metadata
        else:
            raise ConfigFileError(f"Line {line_number}: meta-data bad syntax ")

    def _parse_connection(self, line, line_number):
        connection_pattern = re.compile(r"^(?P<connection>[^\s-]+-[^\s-]+)?"
    r"\s*"
    r"(?P<metadata>\[\w+=\S+(?:\s+\w+=\S+)*\])?"
    r"(?P<garbage>.*)$")
        match = re.match(connection_pattern, line.removeprefix("connection:").strip())
        if match.group("garbage"):
            raise ConfigFileError(f'Line {line_number}: invalid connection syntax <'+ match.group("garbage")+'>')
        else:
            HubA = match.group("connection").split("-")[0]
            HubB = match.group("connection").split("-")[1]
            return Connection(HubA, HubB, match.group("metadata"))


    def parse_data(self):
        hubs = []
        connections: list = []
        with open(self._filename, 'r') as file:
            i = 0
            line_number = 0
            for line in file:
                line_number += 1
                if line == '\n' or line.startswith("#"):
                    continue
                else:
                    if "#" in line:
                        line = line.split("#")[0]
                    # Parse nb_drones
                    if i == 0 and not line.startswith("nb_drones:"):
                        if any(l.startswith("nb_drones:") for l in file) :
                            raise ConfigFileError("The number of drones should be at the first line")
                        elif i == 0 and not line.startswith("nb_drones:"):
                            raise ConfigFileError("Missing the nb_drones line")
                    elif i == 0 and line.startswith("nb_drones:"):
                        str_nb_drones = line.split(":")[1].strip()
                        nb_drones: int = self._parse_positif_int(str_nb_drones, "The number of drones", line_number)
                        i += 1

                    # Parse start_hub
                    elif line.startswith("start_hub:"):
                        if data_checklist["start_hub"] == 0:
                            data_checklist["start_hub"] += 1
                            start_hub = self._parse_hub(line, line_number)
                            start_hub_obj = Hub(**start_hub, is_start=True, is_end=False)
                        else:
                            raise ConfigFileError("There must be exactly one start_hub: zone and one end_hub: zone.")

                    # Parse hubs
                    elif line.startswith("hub:"):
                        hub= self._parse_hub(line, line_number)
                        hubs.append(hub)

                    # Parse end_hub
                    elif line.startswith("end_hub:"):
                        if data_checklist["end_hub"] == 0:
                            data_checklist["end_hub"] += 1
                            end_hub = self._parse_hub(line, line_number)
                            end_hub_obj = Hub(**end_hub, is_start=False, is_end=True)


                    # Parse connexions
                    elif line.startswith("connection"):
                        connections.append(self._parse_connection(line, line_number))

            t_graph = Graph(nb_drones, start_hub_obj, end_hub_obj, hubs, connections)
            return t_graph
