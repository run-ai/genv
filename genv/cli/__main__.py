import argparse
import asyncio
from gettext import gettext as _
import sys

from . import activate
from . import attach
from . import config
from . import deactivate
from . import detach
from . import devices
from . import enforce
from . import envs
from . import home
from . import llm
from . import lock
from . import monitor
from . import remote
from . import shell
from . import status
from . import usage
from . import version


# NOTE(raz): this is needed for modules that their output is being eval() by the
# 'genv' shell function. it is copied almost as-is from argparse.
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


def _is_shell_module(module: str) -> bool:
    """Returns whether a module is a shell module"""

    return module in ["activate", "deactivate"]


def main():
    """
    The genv entrypoint.
    """

    parser = argparse.ArgumentParser(
        description="Query and control Genv on this machine or in a cluster"
    )

    subparsers = parser.add_subparsers(dest="submodule", metavar="SUBCOMMAND")

    for submodule, help, add_arguments in [
        ("activate", "Activate shell environment", activate.add_arguments),
        ("attach", "Attach devices to this environment", attach.add_arguments),
        ("config", "Configure the current environment", config.add_arguments),
        ("deactivate", "Deactivate shell environment", deactivate.add_arguments),
        ("detach", "Attach devices from this environment", detach.add_arguments),
        ("devices", "Query and manage devices", devices.add_arguments),
        ("enforce", "Enforce GPU usage", enforce.add_arguments),
        ("envs", "Query and manage environments", envs.add_arguments),
        (
            "home",
            "Show the home directory of the current environment",
            home.add_arguments,
        ),
        ("llm", "Run and attach to LLMs", llm.add_arguments),
        ("lock", "Lock over-subscribed devices", lock.add_arguments),
        ("monitor", "Monitor using Prometheus and Grafana", monitor.add_arguments),
        ("remote", "Query, manage and monitor remote machines", remote.add_arguments),
        ("shell", "Shell support", shell.add_arguments),
        ("status", "Show status of the current environment", status.add_arguments),
        ("usage", "GPU usage miscellaneous", usage.add_arguments),
        ("version", "Print Genv version", version.add_arguments),
    ]:
        aliases = [f"{submodule}s"] if submodule in ["llm"] else []

        subparser = subparsers.add_parser(
            submodule,
            aliases=aliases,
            help=help,
            add_help=not _is_shell_module(submodule),
        )

        if _is_shell_module(submodule):
            subparser.register("action", "help_stderr", _HelpStderrAction)

            subparser.add_argument(
                "-h",
                "--help",
                action="help_stderr",
                default=argparse.SUPPRESS,
                help=_("show this help message and exit"),
            )

            # this is the process identifier of the shell which is passed by the 'genv'
            # shell function that is installed by "genv shell"
            subparser.add_argument("--shell", type=int, help=argparse.SUPPRESS)

        add_arguments(subparser)

    args = parser.parse_args()

    try:
        if args.submodule is None:
            parser.print_help()
            parser.exit()

        if _is_shell_module(args.submodule) and not args.shell:
            raise RuntimeError(shell.error_msg())

        if args.submodule == "activate":
            activate.run(args.shell, args)
        elif args.submodule == "attach":
            attach.run(args)
        elif args.submodule == "config":
            config.run(args)
        elif args.submodule == "deactivate":
            deactivate.run(args.shell, args)
        elif args.submodule == "detach":
            detach.run(args)
        elif args.submodule == "devices":
            devices.run(args)
        elif args.submodule == "enforce":
            asyncio.run(enforce.run(args))
        elif args.submodule == "envs":
            envs.run(args)
        elif args.submodule == "home":
            home.run(args)
        elif args.submodule in ["llm", "llms"]:
            llm.run(args)
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
        elif args.submodule == "version":
            version.run(args)
    except RuntimeError as e:
        print(e, file=sys.stderr)
        exit(1)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
