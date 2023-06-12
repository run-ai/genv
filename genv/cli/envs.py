import argparse
from typing import Iterable, Optional

import genv

QUERIES = {
    "eid": lambda env: env.eid,
    "creation": lambda env: env.creation,
    "uid": lambda env: env.uid,
    "username": lambda env: env.username,
    "config.name": lambda env: env.config.name,
    "config.gpus": lambda env: env.config.gpus,
    "config.gpu_memory": lambda env: env.config.gpu_memory,
    "pids": lambda env: " ".join(str(pid) for pid in env.pids),
    "kernel_ids": lambda env: " ".join(kernel_id for kernel_id in env.kernel_ids),
}


def do_activate(
    snapshot: genv.Envs,
    eid: str,
    uid: int,
    username: Optional[str],
    pid: Optional[int],
    kernel_id: Optional[str],
) -> None:
    """
    Activates an environment.
    Creates the environment if does not exist already.
    Attaches the given process id or and jupyter kernel ids if exist.
    """
    if eid not in snapshot:
        snapshot.activate(
            eid=eid,
            uid=uid,
            username=username,
        )

    snapshot[eid].attach(pid=pid, kernel_id=kernel_id)


def do_config(
    snapshot: genv.Envs, eid: str, command: str, args: argparse.Namespace
) -> None:
    """
    Update environment config variables - either set a specific variable or clear it.

    :param command: a string describing which variable in the environment config to change
    :param args: parameters for the config change.
                For example - gpus count variable, clear/not clear config variable, etc.
    :return: None
    """
    if eid in snapshot:
        env = snapshot[eid]

        if command == "gpus":
            env.config.gpus = args.count
        elif command == "name":
            env.config.name = args.name
        elif command == "gpu-memory":
            env.config.gpu_memory = args.gpu_memory


def do_deactivate(snapshot: genv.Envs, pid: int) -> None:
    """
    Detaches the given process identifier.
    """
    snapshot.cleanup(poll_pid=lambda pid_: pid_ != pid)


def do_find(snapshot: genv.Envs, pid: Optional[int], kernel_id: Optional[str]) -> None:
    """
    Prints the environment identifiers of the given process or kernel.
    """
    for env in snapshot.find(pid=pid, kernel_id=kernel_id):
        print(env.eid)


def do_ps(snapshot: genv.Envs, format: str, header: bool, timestamp: bool) -> None:
    """
    Print environments data in a human-readable fashion to the stdio.

    :param format: Which format should be used to print the environment data - csv or tui (default: tui).
    :param header: a flag instructing if we should print a header as part of the output (default: print header).
    :param timestamp: a flag instructing if we should print creation time as is or relative duration (now - creation).
                    (default: relative duration)
    :return: None
    """
    if header:
        if format == "csv":
            print("ID,USER,NAME,CREATED,PID(S)")
        elif format == "tui":
            print("ID      USER            NAME            CREATED              PID(S)")

    for env in snapshot:
        eid = env.eid
        user = f"{env.username}({env.uid})" if env.username else env.uid
        name = env.config.name or ""
        created = env.creation if timestamp else genv.utils.time_since(env.creation)
        pids = " ".join(str(pid) for pid in env.pids)
        # TODO(raz): print kernel ids

        if format == "csv":
            print(f"{eid},{user},{name},{created},{pids}")
        elif format == "tui":
            print(f"{eid:<8}{user:<16}{name:<16}{created:<21}{pids}")


def do_query(snapshot: genv.Envs, eid: Optional[str], queries: Iterable[str]) -> None:
    """
    Queries environment data using a query string. The queries results will be printed into the stdio.
    """
    eids = [eid] if eid is not None else snapshot.eids

    for eid in eids:
        if eid not in snapshot:
            continue

        env = snapshot[eid]

        def query(name: str) -> str:
            result = QUERIES[name](env)

            return "" if result is None else str(result)

        print(",".join(query(name) for name in queries))


def add_arguments(parser: argparse.ArgumentParser) -> None:
    """
    Adds "genv envs" arguments to a parser.
    """

    parser.add_argument(
        "--no-cleanup",
        dest="cleanup",
        action="store_false",
        help="Do not perform clean up",
    )

    parser.add_argument("--reset", action="store_true", help="Reset previous state")

    subparsers = parser.add_subparsers(dest="command")

    def activate(parser):
        parser.add_argument("--eid", required=True, help="Environment identifier")
        parser.add_argument(
            "--uid", type=int, required=True, help="User identifier"
        )  # TODO(raz): should we make this optional?
        parser.add_argument("--username", help="User name")

        group = parser.add_mutually_exclusive_group(required=True)

        group.add_argument("--pid", type=int, help="Process identifier")
        group.add_argument("--kernel-id", help="Jupyter kernel identifier")

    def config(parser):
        def gpus(parser):
            group = parser.add_mutually_exclusive_group(required=True)
            group.add_argument("--count", type=int, help="Device count")
            group.add_argument(
                "--clear", action="store_true", help="Clear device count"
            )

        def name(parser):
            group = parser.add_mutually_exclusive_group(required=True)
            group.add_argument("--name", help="Environment name")
            group.add_argument(
                "--clear", action="store_true", help="Clear environment name"
            )

        def gpu_memory(parser):
            group = parser.add_mutually_exclusive_group(required=True)
            group.add_argument("--gpu-memory", help="Environment GPU memory capacity")
            group.add_argument(
                "--clear",
                action="store_true",
                help="Clear environment GPU memory capacity",
            )

        parser.add_argument("--eid", required=True, help="Environment identifier")

        subparsers = parser.add_subparsers(dest="config", required=True)

        for option in [
            (gpus, "Configure device count for environment"),
            (name, "Configure environment name"),
            (gpu_memory, "gpu-memory", "Configure environment GPU memory capacity"),
        ]:
            if len(option) == 2:
                command, help = option
                name_ = command.__name__
            else:
                command, name_, help = option

            command(subparsers.add_parser(name_, help=help))

    def deactivate(parser):
        parser.add_argument("--pid", type=int, required=True, help="Process identifier")

    def find(parser):
        group = parser.add_mutually_exclusive_group(required=True)

        group.add_argument("--pid", type=int, help="Process identifier")
        group.add_argument("--kernel-id", help="Jupyter kernel identifier")

    def ps(parser):
        parser.add_argument(
            "--no-header",
            dest="header",
            action="store_false",
            help="Do not print column headers",
        )
        parser.add_argument(
            "--timestamp", action="store_true", help="Print a non-prettified timestamp"
        )
        parser.add_argument(
            "--format",
            choices=["csv", "tui"],
            help="Output format; CSV or TUI (Text-based user interface)",
            default="tui",
        )

    def query(parser):
        parser.add_argument("--eid", help="Environment identifier")
        parser.add_argument(
            "--query",
            "--queries",
            dest="queries",
            nargs="+",
            choices=QUERIES.keys(),
            required=True,
        )

    for command, help in [
        (activate, "Activate a process or a Jupyter kernel"),
        (config, "Configure an environment"),
        (deactivate, "Deactivate a process or a Jupyter kernel"),
        (find, "Find the environment of a process or a Jupyter kernel"),
        (ps, "Print information about active environments"),
        (query, "Query environments or a specific one"),
    ]:
        command(subparsers.add_parser(command.__name__, help=help))


def run(args: argparse.Namespace) -> None:
    """
    Runs the "genv envs" logic.
    """

    with genv.utils.global_lock():
        with genv.core.envs.State(args.cleanup, args.reset) as envs:
            if args.command == "activate":
                do_activate(
                    envs,
                    args.eid,
                    args.uid,
                    args.username,
                    args.pid,
                    args.kernel_id,
                )
            elif args.command == "config":
                do_config(envs, args.eid, command=args.config, args=args)
            elif args.command == "deactivate":
                do_deactivate(envs, args.pid)
            elif args.command == "find":
                do_find(envs, args.pid, args.kernel_id)
            elif args.command == "ps":
                do_ps(envs, args.format, args.header, args.timestamp)
            elif args.command == "query":
                do_query(envs, args.eid, args.queries)
            else:
                do_ps(envs, format="tui", header=True, timestamp=False)
