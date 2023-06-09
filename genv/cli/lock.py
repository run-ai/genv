import argparse
import subprocess
import sys
from typing import NoReturn

import genv.sdk


def add_arguments(parser: argparse.ArgumentParser) -> None:
    """
    Adds "genv lock" arguments to a parser.
    """

    parser.add_argument(
        "args",
        nargs=argparse.REMAINDER,
        metavar="COMMAND",
        help="Command to run under the device lock",
    )


def run(args: argparse.Namespace) -> NoReturn:
    """
    Runs the "genv lock" logic.
    """

    with genv.sdk.devices.lock():
        status = subprocess.run(args.args).returncode if len(args.args) else 0
        sys.exit(status)
