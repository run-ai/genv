import argparse
import os
import shutil
from typing import Iterable, NoReturn, Optional

import psutil

from genv.entities import Env
import genv.sdk


def _find_port(env: Env) -> Optional[int]:
    """Finds any port an LLM server environment listens on."""

    for pid in env.pids:
        try:
            ports = genv.utils.get_process_listen_ports(pid)

            if len(ports) > 0:
                return ports[0]
        except psutil.NoSuchProcess:
            continue


def _exec_ollama(args: Iterable[str], host: str, port: int) -> NoReturn:
    """
    Executes ollama.
    Raises RuntimeError if ollama is not properly installed.

    :param args: Arguments to pass to ollama.
    :param host: Hostname to pass to ollama.
    :param port: Port to pass to ollama.
    """

    path = shutil.which("ollama")

    if not path:
        raise RuntimeError(
            """\
Could not find ollama.
You should install it if it's not already installed.
Otherwise, $PATH is probably not configured properly."""
        )

    os.execve(path, [path, *args], {"OLLAMA_HOST": f"{host}:{port}", **os.environ})


def do_attach(model: str) -> NoReturn:
    """
    Attaches to a running LLM.
    Raises RuntimeError if could not find the LLM.

    :param model: Model name.
    """

    with genv.utils.global_lock():
        envs = genv.core.envs.snapshot()

    envs = envs.filter(name=f"llm/{model}")

    if len(envs) == 0:
        raise RuntimeError(f"Could not find LLM model '{model}'")

    # TODO(raz): we currently attach to the first replica; we should pick a replica in a smarter way.
    env = next(iter(envs))
    port = _find_port(env)

    if not port:
        raise RuntimeError(f"Could not find port of LLM model '{model}'")

    _exec_ollama(["run", model], host="localhost", port=port)


def do_ps(format: str, header: bool, timestamp: bool) -> None:
    """
    Print LLM data in a human-readable fashion to the stdio.

    :param format: Print format ('csv' or 'tui').
    :param header: Print header row.
    :param timestamp: Print creation time as a timestamp instead of in a human-readable format.

    :return: None
    """
    with genv.utils.global_lock():
        envs = genv.core.envs.snapshot()

    if header:
        if format == "csv":
            print("MODEL,PORT,CREATED,EID,USER,PID(S)")
        elif format == "tui":
            print(
                "MODEL       PORT    CREATED              EID     USER            PID(S)"
            )

    for env in envs:
        if not (env.config.name and env.config.name.startswith("llm/")):
            continue

        model = env.config.name.split("llm/")[1]
        port = _find_port(env) or "N/A"
        created = env.creation if timestamp else genv.utils.time_since(env.creation)
        eid = env.eid
        user = f"{env.username}({env.uid})" if env.username else env.uid
        pids = " ".join(str(pid) for pid in env.pids)

        if format == "csv":
            print(f"{model},{port},{created},{eid},{user}{pids}")
        elif format == "tui":
            print(f"{model:<12}{port:<8}{created:<21}{eid:<8}{user:<16}{pids}")


def do_serve(
    model: str, host: str, port: int, gpus: Optional[int], gpu_memory: Optional[str]
) -> NoReturn:
    """Runs an LLM server in a newly created environment."""

    with genv.sdk.env.activate(
        config=Env.Config(name=f"llm/{model}", gpus=gpus, gpu_memory=gpu_memory)
    ):
        _exec_ollama(["serve"], host=host, port=port)


def add_arguments(parser: argparse.ArgumentParser) -> None:
    """
    Adds "genv llm" arguments to a parser.
    """

    subparsers = parser.add_subparsers(dest="command")

    def attach(parser):
        parser.add_argument("model")

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

    def serve(parser):
        parser.add_argument("model")

        configuration = parser.add_argument_group("configuration")
        configuration.add_argument(
            "--host", default="127.0.0.1", help="Network interface to bind"
        )
        configuration.add_argument(
            "-p", "--port", type=int, default=0, help="Port to bind"
        )

        env = parser.add_argument_group("env")
        env.add_argument("--gpus", type=int, help="Device count")
        env.add_argument("--gpu-memory", help="Device memory capacity (e.g. 4g)")

    for command, help in [
        (attach, "Attach to a running LLM model"),
        (ps, "Print information about active LLMs"),
        (serve, "Start an LLM server"),
    ]:
        command(subparsers.add_parser(command.__name__, help=help))


def run(args: argparse.Namespace) -> None:
    """
    Runs the "genv llm" logic.
    """

    if args.command == "attach":
        do_attach(args.model)
    elif args.command == "ps":
        do_ps(args.format, args.header, args.timestamp)
    elif args.command == "serve":
        do_serve(args.model, args.host, args.port, args.gpus, args.gpu_memory)
    else:
        do_ps(format="tui", header=True, timestamp=False)
