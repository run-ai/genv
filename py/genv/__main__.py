import argparse
import subprocess
import sys
from typing import Iterable, NoReturn

import genv


def do_lock(args: Iterable[str]) -> NoReturn:
    """
    Runs the provided command under the device lock.
    """
    with genv.sdk.devices.lock():
        status = subprocess.run(args).returncode if len(args) else 0
        sys.exit(status)


def parse_args() -> argparse.Namespace:
    """
    Parses the passed arguments.
    """

    def lock(parser: argparse.ArgumentParser):
        parser.add_argument(
            "args",
            nargs=argparse.REMAINDER,
            metavar="COMMAND",
            help="Command to run under the device lock",
        )

    parser = argparse.ArgumentParser(
        description="Query and control Genv on this machine or in a cluster"
    )

    subparsers = parser.add_subparsers(dest="command", metavar="SUBCOMMAND")

    for command, help in [
        (lock, "Lock over-subscribed devices"),
    ]:
        command(subparsers.add_parser(command.__name__, help=help))

    return parser.parse_args()


def main():
    """
    The genvctl entrypoint.
    """

    args = parse_args()

    if args.command == "lock":
        do_lock(args.args)


if __name__ == "__main__":
    main()
