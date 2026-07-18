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
    metadata: dict

@dataclass
class Graph:
    nb_drones: int
    start_hub: Hub
    end_hub: Hub
    hubs: list[Hub]



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


    def parse_data(self, filename):
        with open(filename, 'r') as file:
            i = 0
            meta_data_pattern = re.compile(r"\[(\w+)=(\w+)\]")
            for line_number, line in enumerate(file):
                if line == '\n' or line.startswith("#"):
                    continue
                else:
                    if i == 0 and not line.startswith("nb_drones")
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

                            absolut_num = start_hub["x"].replace("-", "") if start_hub["x"].startswith("-") else start_hub["x"]
                            if not absolut_num.isdigit():
                                raise ConfigFileError("x coordinate support only numbers")
                            if int(start_hub["x"]) < 0:
                                raise ConfigFileError("x coordinate support only positive numbers")
                            if int(start_hub["x"]) == 0 :
                                raise ConfigFileError("x coordinate must be different to 0")
                            try:
                                start_hub["y"] = line.split(":")[1].strip().split(" ")[2]
                            except Exception:
                                raise ConfigFileError("Messing y  coordinates")
                            if '[' in start_hub["y"] or start_hub["y"].isspace():
                                raise ConfigFileError("Messing y  coordinates")
                            absolut_num = start_hub["y"].replace("-", "") if start_hub["y"].startswith("-") else start_hub["y"]
                            if not absolut_num.isdigit():
                                raise ConfigFileError("y coordinate support only numbers")
                            if int(start_hub["y"]) < 0:
                                raise ConfigFileError("y coordinate support only positive numbers")
                            if int(start_hub["y"]) == 0 :
                                raise ConfigFileError("y coordinate must be different to 0")

                        else:
                            raise ConfigFileError("There must be exactly one start_hub: zone and one end_hub: zone.")

                        print(start_hub)





