import argparse
import asyncio
import sys

from . import devices
from . import enforce
from . import envs
from . import monitor
from . import remote
from . import usage


def parse_args() -> argparse.Namespace:
    """
    Parses the passed arguments.
    """

    parser = argparse.ArgumentParser(
        description="Query and control Genv on this machine or in a cluster"
    )

    subparsers = parser.add_subparsers(dest="submodule", metavar="SUBCOMMAND")

    for submodule, help, add_arguments in [
        ("devices", "Query and manage devices", devices.add_arguments),
        ("enforce", "Enforce GPU usage", enforce.add_arguments),
        ("envs", "Query and manage environments", envs.add_arguments),
        ("monitor", "Monitor using Prometheus and Grafana", monitor.add_arguments),
        ("remote", "Query, manage and monitor remote machines", remote.add_arguments),
        ("usage", "GPU usage miscellaneous", usage.add_arguments),
    ]:
        add_arguments(parser=subparsers.add_parser(submodule, help=help))

    return parser.parse_args()


def main():
    """
    The genvctl entrypoint.
    """

    args = parse_args()

    try:
        if args.submodule == "devices":
            devices.run(args)
        elif args.submodule == "enforce":
            asyncio.run(enforce.run(args))
        elif args.submodule == "envs":
            envs.run(args)
        elif args.submodule == "monitor":
            asyncio.run(monitor.run(args))
        elif args.submodule == "remote":
            asyncio.run(remote.run(args))
        elif args.submodule == "usage":
            asyncio.run(usage.run(args))
    except RuntimeError as e:
        print(e, file=sys.stderr)
        exit(1)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
