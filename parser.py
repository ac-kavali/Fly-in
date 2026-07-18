from dataclasses import dataclass
import re

from numpy.ma.core import absolute


class ConfigFileError(Exception):
    def __init__(self, message):
        super().__init__(message)

@dataclass
class Connexion:
    HubA: str
    HubB: str

@dataclass
class Hub:
    name: str
    x: int
    y: int
    metadata: dict | None

@dataclass
class Graph:
    nb_drones: int
    start_hub: Hub
    end_hub: Hub | None
    hubs: list[Hub] | None



data_checklist = {"start_hub": 0,
                 "end_hub": 0
                  }


class Parser:
    def __init__(self, filename):
        self._filename = filename


    @staticmethod
    def _parse_positif_int(string_num: str, data_specification: str, line_number: int):
        absolut_num = string_num[1:] if string_num.startswith("-") else string_num
        if not absolut_num.isdigit():
            raise ConfigFileError(f"Line {line_number}: {data_specification} support only number!")
        elif int(string_num) < 0:
            raise ConfigFileError(f"Line {line_number}: {data_specification} must be a positive number!")
        if int(string_num) == 0:
            raise ConfigFileError(f"Line {line_number}: {data_specification} must be a different to zero!")
        return int(string_num)

    @staticmethod
    def _parse_metadata(line, line_number):
        metadata_part = " ".join(line.split(" ")[4:]).strip()
        metadata = re.match(meta_data_pattern, metadata_part)
        if metadata:
            metadata = re.split(r"[ =]", metadata.group(0))
            metadata = [data.replace("[", "").replace("]", "") for data in metadata]
            total_len = len(metadata[::2])
            print(total_len)
            metadata = dict(zip(metadata[::2], metadata[1::2]))
            if len(metadata) < total_len:
                raise ConfigFileError(f"Line {line_number}: duplicate meta-data specifications")
        else:
            raise ConfigFileError(f"Line {line_number}: meta-data bad syntax ")

    def parse_data(self):
        with open(self._filename, 'r') as file:
            i = 0
            for line_number, line in enumerate(file):
                if line == '\n' or line.startswith("#"):
                    continue
                else:
                    if i == 0 and not line.startswith("nb_drones"):
                        if any(l.startswith("nb_drones") for l in file) :
                            raise ConfigFileError("The number of drones should be at the first line")
                        elif i == 0 and not line.startswith("nb_drones"):
                            raise ConfigFileError("Missing the nb_drones line")

                    elif i == 0 and line.startswith("nb_drones"):
                        str_nb_drones = line.split(":")[1].strip()
                        nb_drones: int = self._parse_positif_int(str_nb_drones, "The number of drones", line_number)
                        i += 1

                    elif line.startswith("start_hub"):
                        if data_checklist["start_hub"] == 0:
                            data_checklist["start_hub"] += 1
                            start_hub = {}

                            try :
                                start_hub["name"] = line.split(":")[1].strip().split(" ")[0]
                            except IndexError:
                                raise ConfigFileError("Messing Hub name")
                            if meta_data_pattern.match(start_hub["name"]):
                                raise ConfigFileError("Metadata must be after coordinates")

                            if start_hub["name"].isdigit():
                                raise ConfigFileError("Hub name can't be number")

                            if "-" in start_hub["name"]:
                                raise ConfigFileError("dashes are forbidden in hubs name")
                            print(start_hub["name"])

                            try:
                                start_hub["x"] = line.split(":")[1].strip().split(" ")[1]
                            except IndexError :
                                raise ConfigFileError("Missing x and y")

                            start_hub["x"] = self._parse_positif_int(start_hub["x"], "x coordinate", line_number)

                            try:
                                start_hub["y"] = line.split(":")[1].strip().split(" ")[2]
                            except Exception:
                                raise ConfigFileError("Messing y  coordinates")
                            if '[' in start_hub["y"] or start_hub["y"].isspace():
                                raise ConfigFileError("Messing y  coordinates")
                            start_hub["y"] = self._parse_positif_int(start_hub["y"], "y coordinate", line_number)

                            if len(line.strip().split(" ")) > 4 :
                                self.parse


                            t_hub = Hub(**start_hub)


                        else:
                            raise ConfigFileError("There must be exactly one start_hub: zone and one end_hub: zone.")

            t_graph = Graph(nb_drones, t_hub, None, None)
            return t_graph