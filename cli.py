"""Command-line argument parsing utilities."""

from argparse import ArgumentParser, Namespace


def create_parser() -> ArgumentParser:
    """Create an empty argument parser.

    Returns:
        ArgumentParser: A new, unconfigured argument parser instance.
    """
    parser = ArgumentParser()
    return parser


def cla_parser() -> Namespace:
    """Build the CLI parser and parse the command-line arguments.

    Returns:
        Namespace: The parsed command-line arguments, containing the
        `map` attribute with the path to the map file.
    """
    parser = create_parser()
    parser.add_argument("map", type=str, help="The map file path")
    return parser.parse_args()
