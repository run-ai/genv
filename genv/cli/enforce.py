import argparse
import asyncio

import genv


def add_arguments(parser: argparse.ArgumentParser) -> None:
    """
    Adds "genv enforce" arguments to a parser.
    """

    parser.add_argument(
        "--interval",
        type=int,
        default=10,
        help="interval in seconds between enforcement cycles; 0 means run once (default: %(default)s)",
    )

    enforcements = parser.add_argument_group("enforcements")

    def add_enforcement(
        name: str, *, dest: str, help: str, default: bool = True
    ) -> None:
        """
        Adds a mutual exclusive group for an enforcement flag with true and false actions.
        """
        group = enforcements.add_mutually_exclusive_group()

        group.add_argument(
            f"--{name}",
            action="store_true",
            default=default,
            help=help + " (default: %(default)s)",
            dest=dest,
        )

        group.add_argument(
            f"--no-{name}",
            action="store_false",
            dest=dest,
        )

    add_enforcement(
        "non-env-processes",
        dest="non_env_processes",
        help="terminate processes that are not running in a GPU environment",
        default=False,
    )

    add_enforcement(
        "env-devices",
        dest="env_devices",
        help="enforce environment attached devices",
        default=True,
    )

    add_enforcement(
        "env-memory",
        dest="env_memory",
        help="enforce environment memory capacity if set",
        default=True,
    )

    enforcements.add_argument(
        "--max-devices-per-user",
        type=int,
        help="maximum allowed attached devices for each user",
    )

    def max_devices_for_user(value: str):
        try:
            username, maximum = value.split("=")

            return username, int(maximum)
        except (ValueError, SyntaxError):
            raise argparse.ArgumentTypeError(f"not a valid spec: {value}")

    enforcements.add_argument(
        "--max-devices-for-user",
        nargs="+",
        help="per-user specification of maximum allowed attached devices",
        metavar="username=maximum",
        type=max_devices_for_user,
    )


async def run(args: argparse.Namespace) -> None:
    """
    Runs the "genv enforce" logic.
    """

    while True:
        with genv.utils.global_lock():
            snapshot = await genv.core.snapshot()

        survey = genv.entities.enforce.Survey(snapshot)

        if args.non_env_processes:
            genv.enforce.rules.non_env_processes(survey)

        if args.env_devices:
            genv.enforce.rules.env_devices(survey)

        if args.env_memory:
            genv.enforce.rules.env_memory(survey)

        if args.max_devices_per_user is not None:
            genv.enforce.rules.max_devices_per_user(
                survey,
                maximum=args.max_devices_per_user,
                maximum_for_user=(
                    dict(args.max_devices_for_user) if args.max_devices_for_user else {}
                ),
            )

        with genv.utils.global_lock():
            genv.enforce.execute(survey.report)

        if args.interval == 0:
            break

        await asyncio.sleep(args.interval)
