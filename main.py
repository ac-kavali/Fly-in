from models import ZoneType, Hub
from parser import Parser
from path_finding import ReservationTable, Pathfinder
from cli import cla_parser
import sys


try:
    arguments = cla_parser()
    parser = Parser(arguments.map)
    graph = parser.parse_data()
except Exception as e:
    print(e)
    sys.exit(1)

def main() -> None:
    """
    start the program
    return: None
    """


    reservations = ReservationTable(graph) #the reservation table empty

    pathfinder = Pathfinder() # dijkstra pathfinder respect res-table


    total_turns = 0   # turns
    all_paths: list[list[tuple[Hub, int]]] = []    # Example [[(Zone1, turn1), (Zone2, Turn2)..] [anotherpath...3]]

    for drone_id in range(1, graph.nb_drones + 1):
        path = pathfinder.find_path(
            graph,
            graph.start_zone,
            graph.end_zone,
            graph.nb_drones,
            reservations
        )
        print(path)
        obj_path = graph.path_of_zone_obj(path, graph)   # The full paths of all the drones

        if not path:
            print(f"Drone {drone_id}: No path found")
            continue

        all_paths.append(obj_path)
        print(f"All paths: {all_paths}")
        total_turns = path[-1][1]
        print(f"total_turns:{total_turns} ")
        for i, (zone, turn) in enumerate(path):
            reservations.reserve(zone, turn)
            if i == 0:               # If it's the start then it have not previous zone then continue
                continue
            prev_zone, _ = path[i - 1]  #Skip it if its was just waiting
            if zone == prev_zone:
                continue
            obj_zone = graph.get_object_zone(zone)
            if obj_zone is None:
                continue
            movement_cost = obj_zone.get_movement_cost()
            reservation_start = turn - movement_cost + 1
            reservation_end = turn

            for t in range(reservation_start, reservation_end + 1):
                print(f"Turn: {turn}-movement_cost{movement_cost}+1, turn:{turn} +1 ")
                reservations.reserve_connection(
                    prev_zone,
                    zone,
                    t
                )