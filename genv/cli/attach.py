import argparse

import genv.sdk


def add_arguments(parser: argparse.ArgumentParser) -> None:
    """
    Adds "genv attach" arguments to a parser.
    """

    modes = parser.add_argument_group("modes")
    group = modes.add_mutually_exclusive_group()
    group.add_argument(
        "--config",
        action="store_true",
        default=True,
        help="Use device count from configuration (default)",
    )
    group.add_argument(
        "--count", type=int, help="Total number of devices to be attached"
    )
    group.add_argument(
        "--index", type=int, help="Attach to the device with the given index"
    )
    group.add_argument(
        "--refresh", action="store_true", help="Only refresh attachments"
    )

    options = parser.add_argument_group("options")
    options.add_argument(
        "-o",
        "--over-subscribe",
        dest="allow_over_subscription",
        action="store_true",
        help="Use unavailable devices if needed",
    )


def run(args: argparse.Namespace) -> None:
    """
    Runs the "genv attach" logic.
    """

    if not genv.sdk.active():
        raise RuntimeError("Not running in an active environment")

    if not args.refresh:
        genv.sdk.attach(
            index=args.index,
            gpus=args.count,
            allow_over_subscription=args.allow_over_subscription,
        )
