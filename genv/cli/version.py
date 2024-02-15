import argparse
import pkg_resources


def add_arguments(parser: argparse.ArgumentParser) -> None:
    """Adds "genv version" arguments to a parser."""

    pass


def run(args: argparse.Namespace) -> None:
    """Runs the "genv version" logic."""

    print(pkg_resources.get_distribution("genv").version)
