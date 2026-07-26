"""Terminal output utilities for printing the drone simulation."""

from models import Hub, ZoneType, Graph


class TerminalOutput:
    """Handles terminal output for the simulation."""

    def print_simulation(
        self,
        all_paths: list[list[tuple[Hub, int]]],
        total_turns: int,
        graph: Graph
    ) -> None:
        """Print the complete simulation turn by turn.

        Args:
            all_paths: Paths followed by all drones.
            total_turns: Total number of turns in the simulation.
            graph: Map graph object.

        Returns:
            None
        """
        movements_by_turn: dict[int, list[str]] = {}

        for drone_id, path in enumerate(all_paths, start=1):
            for i, (hub, turn) in enumerate(path):

                if i == 0:
                    continue

                prev_hub, _ = path[i - 1]

                if hub == prev_hub:
                    continue

                if graph.get_movement_cost(hub) == 2:
                    if turn - 1 not in movements_by_turn:
                        movements_by_turn[turn - 1] = []

                    prev_name = self.colorize_zone_name(prev_hub)
                    hub_name = self.colorize_zone_name(hub)
                    movements_by_turn[turn - 1].append(
                        f"D{drone_id}-{prev_name}-{hub_name}"
                    )

                if turn not in movements_by_turn:
                    movements_by_turn[turn] = []

                movements_by_turn[turn].append(
                    f"D{drone_id}-{self.colorize_zone_name(hub)}"
                )

        for turn in sorted(movements_by_turn):
            self.print_turn(turn, movements_by_turn[turn])

        self.print_summary(total_turns)

    def print_turn(self, turn: int, movements: list[str]) -> None:
        """Print all drone movements for one simulation turn.

        Args:
            turn: Current simulation turn.
            movements: Drone movements performed during the turn.

        Returns:
            None
        """
        print(f"Turn {turn}: {' '.join(movements)}")

    def print_summary(self, total_turns: int) -> None:
        """Print the total number of turns.

        Args:
            total_turns: Total turns required to finish the
                simulation.

        Returns:
            None
        """
        print(f"\nTotal turns: {total_turns}")

    def colorize_zone_name(self, hub: Hub) -> str:
        """Return hub.name wrapped in an ANSI color code.

        Priority:
            1. Use the zone's explicit metadata color if one was set.
            2. Otherwise, fall back to a color based on the zone
               type.

        Args:
            hub: The hub whose name should be colorized.

        Returns:
            str: The hub's name wrapped in ANSI color escape codes.
        """
        reset = "\033[0m"

        if hub.metadata.color is not None:
            color_by_name = {
                "red": "\033[31m",
                "green": "\033[32m",
                "yellow": "\033[33m",
                "blue": "\033[34m",
                "magenta": "\033[35m",
                "cyan": "\033[36m",
                "gray": "\033[90m",
                "grey": "\033[90m",
                "white": "\033[97m",
            }
            prefix = color_by_name.get(hub.metadata.color.lower(), "\033[37m")
        else:
            prefix_by_type = {
                ZoneType.RESTRICTED: "\033[31m",  # red
                ZoneType.PRIORITY: "\033[32m",  # green
                ZoneType.BLOCKED: "\033[90m",  # gray
                ZoneType.NORMAL: "\033[37m",  # white/default
            }
            prefix = prefix_by_type.get(hub.metadata.zone, "\033[37m")

        return f"{prefix}{hub.name}{reset}"
