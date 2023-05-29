import argparse
import sys

from . import lock


def parse_args() -> argparse.Namespace:
    """
    Parses the passed arguments.
    """

    parser = argparse.ArgumentParser(description="Use Genv within an environment")

    subparsers = parser.add_subparsers(dest="submodule", metavar="SUBCOMMAND")

    for submodule, help, add_arguments in [
        ("lock", "Lock over-subscribed devices", lock.add_arguments),
    ]:
        add_arguments(parser=subparsers.add_parser(submodule, help=help))

    return parser.parse_args()


def main():
    """
    The genvsdk entrypoint.
    """

    args = parse_args()

    try:
        if args.submodule == "lock":
            lock.run(args)
    except RuntimeError as e:
        print(e, file=sys.stderr)
        exit(1)


if __name__ == "__main__":
    main()
