"""Entry point for running the drone pathfinding simulation.

This module loads the map data, computes conflict-free paths for each
drone using a reservation-table-aware pathfinder, and prints the
resulting simulation to the terminal.
"""

import sys

from models import Hub
from parser import Parser
from path_finding import ReservationTable, Pathfinder
from cli import cla_parser
from terminal_output import TerminalOutput


try:
    arguments = cla_parser()
    parser = Parser(arguments.map)
    graph = parser.parse_data()
except Exception as e:
    print(e)
    sys.exit(1)


def main() -> None:
    """Compute and print conflict-free paths for all drones.

    Iterates over every drone, requests a path from the pathfinder
    while respecting the shared reservation table, reserves the zones
    and connections used by that path, and finally prints the full
    simulation summary to the terminal.

    Returns:
        None
    """
    reservations = ReservationTable(graph)
    pathfinder = Pathfinder()
    terminal_print = TerminalOutput()

    total_turns = 0
    all_paths: list[list[tuple[Hub, int]]] = []

    for drone_id in range(1, graph.nb_drones + 1):
        path = pathfinder.find_path(
            graph,
            graph.start_hub,
            graph.end_hub,
            graph.nb_drones,
            reservations
        )
        obj_path = graph.path_of_zone_obj(path)

        if not path:
            print(f"Drone {drone_id}: No path found")
            continue

        all_paths.append(obj_path)
        total_turns = path[-1][1]
        for i, (zone, turn) in enumerate(path):
            reservations.reserve(zone, turn)
            if i == 0:
                continue
            prev_zone, _ = path[i - 1]
            if zone == prev_zone:
                continue
            obj_zone = graph.get_zone_by_name(zone)
            if obj_zone is None:
                continue

            movement_cost = graph.get_movement_cost(obj_zone)
            if movement_cost is None:
                continue
            reservation_start: int = turn - movement_cost + 1
            reservation_end: int = turn

            for t in range(reservation_start, reservation_end + 1):
                reservations.reserve_connection(
                    prev_zone,
                    zone,
                    t
                )

    terminal_print.print_simulation(all_paths, total_turns, graph)


if __name__ == "__main__":
    main()
