import re

from numpy.ma.core import absolute

from models import (
    ZoneType, ConfigFileError, Connection, HubMetadata, Hub, Graph
)


class Parser:
    def __init__(self, filename):
        self._filename = filename
        self.meta_data_pattern = re.compile(r"\[(\w+=\S+)(\s+\w+=\S+)*\]")
        self.valid_m_keys = {"zone", "color", "max_drones"}
        self.check_conn = set()
        self.reserved_zone_names = set()
        self.data_checklist = {"start_hub": 0, "end_hub": 0}
        self.all_coordinates = set()

    @staticmethod
    def _parse_positif_int(string_num: str, data_spec: str, line_number: int):
        absolute_num = string_num
        if string_num.startswith("-") or string_num.startswith("+"):
            absolute_num = string_num[1:]
        if not absolute_num.isdigit():
            raise ConfigFileError(
                f"Line {line_number}: {data_spec} support only number!"
            )
        if "number of drones" in data_spec:
            if int(string_num) == 0:
                raise ConfigFileError(
                    f"Line {line_number}: {data_spec} must be a "
                    "different to zero!"
                )
            elif int(string_num) < 0:
                raise ConfigFileError(
                    f"Line {line_number}: {data_spec} must be a "
                    "positive number!"
                )
        return int(string_num)

    def _parse_hub(self, line, line_number):
        hub = {}
        try:
            hub["name"] = line.split(":")[1].strip().split()[0]
        except IndexError:
            raise ConfigFileError("Messing Hub name")
        if self.meta_data_pattern.match(hub["name"]):
            raise ConfigFileError("Metadata must be after coordinates")

        if "-" in hub["name"]:
            raise ConfigFileError("dashes are forbidden in hubs name")

        # Parse x
        try:
            hub["x"] = line.split(":")[1].strip().split()[1]
        except IndexError:
            raise ConfigFileError("Missing x and y")

        hub["x"] = self._parse_positif_int(
            hub["x"], "x coordinate", line_number
        )

        # Parse y
        try:
            hub["y"] = line.split(":")[1].strip().split()[2]
        except Exception:
            raise ConfigFileError("Messing y  coordinates")
        if '[' in hub["y"] or hub["y"].isspace():
            raise ConfigFileError("Messing y  coordinates")
        hub["y"] = self._parse_positif_int(
            hub["y"], "y coordinate", line_number
        )

        # Parse meta-data
        if len(line.strip().split(" ")) > 4:
            hub["metadata"]: HubMetadata = self._parse_metadata(
                line, line_number
            )
        else:
            hub["metadata"] = HubMetadata()
        if hub["name"] in self.reserved_zone_names:
            raise ConfigFileError(
                f'Line {line_number}: duplicate zone name \'{hub["name"]}\''
            )
        self.reserved_zone_names.add(hub["name"])
        coords = (hub["x"], hub["y"])
        if coords in self.all_coordinates:
            raise ConfigFileError(f"Line {line_number} duplicate coordinates")
        self.all_coordinates.add(coords)
        return hub

    def _parse_metadata(
            self, line: str, line_number: int
    ) -> HubMetadata:
        metadata_part = " ".join(line.split()[4:]).strip()
        match = re.match(self.meta_data_pattern, metadata_part)

        if not match:
            raise ConfigFileError(
                f"Line {line_number}: meta-data bad syntax"
            )

        tokens = re.split(r"[ =]", match.group(0))
        tokens = [tok.replace("[", "").replace("]", "") for tok in tokens]
        keys = tokens[::2]
        values = tokens[1::2]

        if len(set(keys)) < len(keys):
            raise ConfigFileError(
                f"Line {line_number}: duplicate meta-data specifications"
            )

        parsed = dict(zip(keys, values))
        invalid_meta = set(parsed) - self.valid_m_keys
        if invalid_meta:
            raise ConfigFileError(
                f"Line {line_number}: invalid metadata "
                f"keys({next(iter(invalid_meta))})"
            )
        kwargs: dict[str, ZoneType | str | int] = {}
        try:
            if "zone" in parsed:
                kwargs["zone"] = ZoneType(parsed["zone"])
            if "color" in parsed:
                kwargs["color"] = parsed["color"]
            if "max_drones" in parsed:
                kwargs["max_drones"] = int(parsed["max_drones"])
        except ValueError as exc:
            raise ConfigFileError(
                f"Line {line_number}: invalid meta-data value ({exc})"
            ) from exc
        if "max_drones" in parsed:
            if not ("start_hub" in line or "end_hub" in line):
                if int(kwargs["max_drones"]) < 1 :
                    raise ConfigFileError(
                        f"Line {line_number}: Max drones can't be "
                        "negative (default=1)!"
                    )
        return HubMetadata(**kwargs)

    def _parse_connection(self, line, line_number):
        if not line.strip().split(":")[1]:
            raise ConfigFileError(
                f"Line {line_number}: Invalid connection syntax"
            )
        connection_pattern = re.compile(
            r"^(?P<connection>[^\s-]+-[^\s-]+)?"
            r"\s*"
            r"(?P<metadata>\[max_link_capacity=[+-]?\d+\])?"
            r"(?P<garbage>.*)$"
        )
        max_link_capacity = 1
        match = re.match(
            connection_pattern, line.removeprefix("connection:").strip()
        )
        if match.group("garbage"):
            raise ConfigFileError(
                f'Line {line_number}: invalid connection syntax <'
                + match.group("garbage") + '>'
            )
        else:
            HubA = match.group("connection").split("-")[0]
            HubB = match.group("connection").split("-")[1]
            self._check_zone_name(HubA, line_number)
            self._check_zone_name(HubB, line_number)
            current_connection = frozenset((HubA, HubB))
            if current_connection in self.check_conn:
                raise ConfigFileError(
                    f"Line {line_number}: duplicate connection! "
                )
            else:
                self.check_conn.add(current_connection)
                if match.group("metadata"):
                    max_link_capacity = (
                        match.group("metadata")
                        .replace("[", "")
                        .replace("]", "")
                        .split("=")[1]
                    )
                max_link_capacity=int(max_link_capacity)
                if max_link_capacity < 1 :
                    raise ConfigFileError(f"Line {line_number}: max capacity cant be zero or negative (default=1)")
                return Connection(HubA, HubB, max_link_capacity)

    def _check_zone_name(self, zone_name, line_number):
        if zone_name not in self.reserved_zone_names:
            raise ConfigFileError(
                f"Line {line_number}: <{zone_name}> not a valid hub "
            )

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
                        if any(
                            ln.startswith("nb_drones:") for ln in file
                        ):
                            raise ConfigFileError(
                                "The number of drones should be at "
                                "the first line"
                            )
                        elif i == 0 and not line.startswith("nb_drones:"):
                            raise ConfigFileError(
                                "Missing the nb_drones line"
                            )
                    elif i == 0 and line.startswith("nb_drones:"):
                        str_nb_drones = line.split(":")[1].strip()
                        nb_drones: int = self._parse_positif_int(
                            str_nb_drones, "The number of drones",
                            line_number
                        )
                        i += 1

                    # Parse start_hub
                    elif line.startswith("start_hub:"):
                        if self.data_checklist["start_hub"] == 0:
                            self.data_checklist["start_hub"] += 1
                            start_hub: dict = self._parse_hub(
                                line, line_number
                            )
                            start_hub_obj = Hub(
                                start_hub["name"],
                                start_hub["x"],
                                start_hub["y"],
                                is_start=True,
                                is_end=False,
                                metadata=start_hub["metadata"]
                                or HubMetadata()
                            )
                        else:
                            raise ConfigFileError(
                                "There must be exactly one start_hub: "
                                "zone and one end_hub: zone."
                            )

                    # Parse hubs
                    elif line.startswith("hub:"):
                        hub = self._parse_hub(line, line_number)
                        hub_obj = Hub(
                            hub["name"], hub["x"], hub["y"],
                            is_start=True, is_end=False,
                            metadata=hub["metadata"] or HubMetadata()
                        )
                        hubs.append(hub_obj)

                    # Parse end_hub
                    elif line.startswith("end_hub:"):
                        if self.data_checklist["end_hub"] == 0:
                            self.data_checklist["end_hub"] += 1
                            end_hub = self._parse_hub(line, line_number)
                            end_hub_obj = Hub(
                                end_hub["name"], end_hub["x"], end_hub["y"], is_start=False, is_end=True, metadata=end_hub["metadata"]
                            )

                    # Parse connexions
                    elif line.startswith("connection"):
                        connections.append(
                            self._parse_connection(line, line_number)
                        )

            if (self.data_checklist["start_hub"] != 1
                    or self.data_checklist["end_hub"] != 1):
                raise ConfigFileError(
                    "Config file error : There must be exactly one "
                    "start_hub: zone and one end_hub: zone."
                )

            self.data_checklist = {"start_hub": 0, "end_hub": 0}

            t_graph = Graph(
                nb_drones, start_hub_obj, end_hub_obj, hubs, connections
            )
            return t_graph