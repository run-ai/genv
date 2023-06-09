import argparse
import json
import sys
from typing import Optional

import genv

# TODO(raz): should this executable be merged to remote.py


async def do_execute() -> None:
    report = json.loads(sys.stdin.read(), cls=genv.JSONDecoder)

    with genv.utils.global_lock():
        genv.enforce.execute(report)


async def do_snapshot(format: str, type: Optional[str]) -> None:
    with genv.utils.global_lock():
        if type is None:
            snapshot = await genv.core.snapshot()
        elif type == "devices":
            snapshot = genv.core.devices.snapshot()
        elif type == "envs":
            snapshot = genv.core.envs.snapshot()
        elif type == "processes":
            snapshot = await genv.core.processes.snapshot()
        else:
            raise ValueError(f"Unsupported snapshot type ({type})")

    if format == "json":
        print(json.dumps(snapshot, cls=genv.JSONEncoder, indent=2))


def add_arguments(parser: argparse.ArgumentParser) -> None:
    """
    Adds "genv usage" arguments to a parser.
    """

    subparsers = parser.add_subparsers(dest="command", required=True)

    def execute(parser):
        pass

    def snapshot(parser):
        parser.add_argument(
            "--format",
            choices=["json"],
            help="Output format (%(choices)s)",
            default="json",
        )

        parser.add_argument(
            "--type",
            choices=["devices", "envs", "processes"],
            help="Take a snapshot of specific information",
        )

    for command, help in [
        (execute, "Execute the report passed in stdin"),
        (snapshot, "Take a snapshot of GPU usage"),
    ]:
        command(subparsers.add_parser(command.__name__, help=help))


async def run(args: argparse.Namespace) -> None:
    """
    Runs the "genv usage" logic.
    """

    if args.command == "execute":
        await do_execute()
    elif args.command == "snapshot":
        await do_snapshot(args.format, args.type)
