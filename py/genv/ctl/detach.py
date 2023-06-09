import argparse

import genv.sdk


def add_arguments(parser: argparse.ArgumentParser) -> None:
    """
    Adds "genvctl detach" arguments to a parser.
    """

    parser.add_argument("--index", type=int, help="Device index to detach from")


def run(args: argparse.Namespace) -> None:
    """
    Runs the "genvctl detach" logic.
    """

    if not genv.sdk.active():
        raise RuntimeError("Not running in an active environment")

    genv.sdk.detach(args.index)
