import argparse
import asyncio
from gettext import gettext as _
import sys

from . import activate
from . import config
from . import devices
from . import enforce
from . import envs
from . import home
from . import lock
from . import monitor
from . import remote
from . import shell
from . import status
from . import usage


# NOTE(raz): this is needed for modules that their output is being eval() by the
# 'genvctl' shell function. it is copied almost as-is from argparse.
class _HelpStderrAction(argparse.Action):
    def __init__(
        self,
        option_strings,
        dest=argparse.SUPPRESS,
        default=argparse.SUPPRESS,
        help=None,
    ):
        super(_HelpStderrAction, self).__init__(
            option_strings=option_strings,
            dest=dest,
            default=default,
            nargs=0,
            help=help,
        )

    def __call__(self, parser, namespace, values, option_string=None):
        parser.print_help(file=sys.stderr)
        parser.exit()


def main():
    """
    The genvctl entrypoint.
    """

    parser = argparse.ArgumentParser(
        description="Query and control Genv on this machine or in a cluster"
    )

    subparsers = parser.add_subparsers(dest="submodule", metavar="SUBCOMMAND")

    for submodule, help, add_arguments in [
        ("activate", "Activate shell environment", activate.add_arguments),
        ("config", "Configure the current environment", config.add_arguments),
        ("devices", "Query and manage devices", devices.add_arguments),
        ("enforce", "Enforce GPU usage", enforce.add_arguments),
        ("envs", "Query and manage environments", envs.add_arguments),
        (
            "home",
            "Show the home directory of the current environment",
            home.add_arguments,
        ),
        ("lock", "Lock over-subscribed devices", lock.add_arguments),
        ("monitor", "Monitor using Prometheus and Grafana", monitor.add_arguments),
        ("remote", "Query, manage and monitor remote machines", remote.add_arguments),
        ("shell", "Shell support", shell.add_arguments),
        ("status", "Show status of the current environment", status.add_arguments),
        ("usage", "GPU usage miscellaneous", usage.add_arguments),
    ]:
        is_shell_submodule = submodule in ["activate"]

        subparser = subparsers.add_parser(
            submodule, help=help, add_help=not is_shell_submodule
        )

        if is_shell_submodule:
            subparser.register("action", "help_stderr", _HelpStderrAction)

            subparser.add_argument(
                "-h",
                "--help",
                action="help_stderr",
                default=argparse.SUPPRESS,
                help=_("show this help message and exit"),
            )

            # this is the process identifier of the shell which is passed by the 'genvctl'
            # shell function that is installed by "genvctl shell"
            subparser.add_argument("--shell", type=int, help=argparse.SUPPRESS)

        add_arguments(subparser)

    args = parser.parse_args()

    try:
        if args.submodule is None:
            parser.print_help()
        elif args.submodule == "activate":
            if not args.shell:
                raise RuntimeError(shell.error_msg())

            activate.run(args.shell, args)
        elif args.submodule == "config":
            config.run(args)
        elif args.submodule == "devices":
            devices.run(args)
        elif args.submodule == "enforce":
            asyncio.run(enforce.run(args))
        elif args.submodule == "envs":
            envs.run(args)
        elif args.submodule == "home":
            home.run(args)
        elif args.submodule == "lock":
            lock.run(args)
        elif args.submodule == "monitor":
            asyncio.run(monitor.run(args))
        elif args.submodule == "remote":
            asyncio.run(remote.run(args))
        elif args.submodule == "shell":
            shell.run(args)
        elif args.submodule == "status":
            status.run(args)
        elif args.submodule == "usage":
            asyncio.run(usage.run(args))
    except RuntimeError as e:
        print(e, file=sys.stderr)
        exit(1)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
