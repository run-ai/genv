import argparse

import genv.sdk


def add_arguments(parser: argparse.ArgumentParser) -> None:
    """
    Adds "genv home" arguments to a parser.
    """

    parser.add_argument("-q", "--quiet", action="store_true")


def run(args: argparse.Namespace) -> None:
    """
    Runs the "genv home" logic.
    """

    home = genv.sdk.home()

    if home:
        print(home)
    elif not args.quiet:
        raise RuntimeError(
            """\
Could not find any Genv configuration directory.

Create a directory named '.genv' under one of the following directories:
  1) Current working directory (i.e. $PWD)
  2) Home directory (i.e. $HOME)
"""
        )
