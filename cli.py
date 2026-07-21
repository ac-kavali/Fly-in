from argparse import ArgumentParser


def create_parser() -> ArgumentParser:
    parser = ArgumentParser()
    return parser


def cla_parser():
    parser = create_parser()
    parser.add_argument("map", type=str, help="The map file path")
    return parser.parse_args()