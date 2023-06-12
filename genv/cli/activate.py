import argparse
import getpass
import os

import genv.utils
from genv.entities import Env
import genv.core
import genv.sdk


def add_arguments(parser: argparse.ArgumentParser) -> None:
    """
    Adds "genv activate" arguments to a parser.
    """

    arguments = parser.add_argument_group("arguments")
    arguments.add_argument("--eid", "--id", help="Environment identifier")

    configure = parser.add_argument_group("configure")
    configure.add_argument("--name", help="Environment name")
    configure.add_argument(
        "--gpu-memory", help="Environment device memory capacity (e.g. 4g)"
    )
    configure.add_argument("--gpus", type=int, help="Environment device count")

    options = parser.add_argument_group("options")
    options.add_argument(
        "--no-prompt",
        action="store_false",
        dest="prompt",
        help="Don't change the prompt",
    )
    options.add_argument(
        "--no-attach",
        action="store_false",
        dest="attach",
        help="Don't attach to devices",
    )
    options.add_argument(
        "-o",
        "--over-subscribe",
        dest="allow_over_subscription",
        action="store_true",
        help="Use unavailable devices if needed",
    )

    load = options.add_mutually_exclusive_group()
    load.add_argument(
        "--no-load",
        action="store_false",
        dest="load",
        help="Don't load configuration from disk (default)",
    )


def run(shell: int, args: argparse.Namespace) -> None:
    """
    Runs the "genv activate" logic.
    """

    if genv.sdk.active():
        raise RuntimeError("Already running in an active environment")

    eid = args.eid or str(shell)

    with genv.utils.global_lock():
        genv.core.envs.activate(
            eid, uid=os.getuid(), username=getpass.getuser(), pid=shell
        )

        # NOTE(raz): we currently override the entire configuration if any
        # configuration field was specified
        if args.name or args.gpu_memory or args.gpus:
            genv.core.envs.configure(
                eid, Env.Config(args.name, args.gpu_memory, args.gpus)
            )

        if args.gpus and args.attach:
            genv.core.devices.attach(
                eid,
                gpus=args.gpus,
                gpu_memory=args.gpu_memory,
                allow_over_subscription=args.allow_over_subscription,
            )

    print(
        f"""
_genv_set_env GENV_SHELL 1
_genv_set_env GENV_ENVIRONMENT_ID {eid}
_genv_replace_env PATH "{os.path.realpath(os.path.join(os.path.dirname(__file__), "../shims"))}:$PATH"

eval "$(command genv shell --reconfigure)"
eval "$(command genv shell --reattach)"
"""
    )

    if args.prompt:
        print('_genv_replace_env PS1 "(genv) ${PS1-}"')
