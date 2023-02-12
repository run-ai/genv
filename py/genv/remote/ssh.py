import asyncio
from dataclasses import dataclass
import os
import sys
from typing import Any, Callable, Iterable, Optional, Tuple

from .utils import reprint


@dataclass
class Host:
    """
    Host configuration.

    :param hostname: Hostname or IP address
    :param root: Genv installation directory
    :param timeout: SSH connection timeout
    """

    hostname: str
    root: str
    timeout: Optional[int]


@dataclass
class Config:
    """
    Execution configuration.

    :param hosts: Host configurations
    :param throw_on_error: Raise 'RuntimeError' if failing to connect to any host
    :param quiet: Ignore SSH errors
    """

    hosts: Iterable[Host]
    throw_on_error: bool
    quiet: bool

@dataclass
class Command:
    """
    Genv command specification.

    :param args: Genv command arguments
    :param sudo: Run command as root using sudo
    """

    args: Iterable[str]
    sudo: bool = False


async def start(host: Host, command: Command, stdin: int) -> asyncio.subprocess.Process:
    """
    Starts a background process that runs a Genv command on a remote host over SSH.

    :param host: Host configuration
    :param command: Genv command specification
    :param stdin: Standard input

    :return: Returns the SSH process
    """
    args = []

    if host.timeout is not None:
        args.append(f"-o ConnectTimeout={host.timeout}")

    path = f"$PATH:{host.root}/bin"

    # add development shims to remote $PATH if in the local $PATH
    if os.path.realpath(os.path.join(os.environ["GENV_ROOT"], "devel/shims")) in [
        os.path.realpath(path) for path in os.environ["PATH"].split(":")
    ]:
        path = f"{path}:{host.root}/devel/shims"

    cmd = f'env PATH="{path}" genv {" ".join(command.args)}'

    if command.sudo:
        cmd = f"sudo {cmd}"

    return await asyncio.create_subprocess_exec(
        "ssh",
        *args,
        host.hostname,
        cmd,
        stdin=stdin,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )


async def run(
    config: Config, command: Command, stdins: Optional[Iterable[str]] = None
) -> Tuple[Iterable[Host], Iterable[str]]:
    """
    Runs a Genv command on multiple hosts over SSH.
    Waits for the command to finish on all hosts.
    Raises 'RuntimeError' if failed to connect to any of the hosts and 'config.throw_on_error' is True.

    :param config: Execution configuration
    :param command: Genv command specification
    :param stdins: Input to send per host

    :return: Returns the hosts that succeeded and their standard outputs
    """
    processes = [
        await start(
            host,
            command,
            asyncio.subprocess.PIPE if stdins else asyncio.subprocess.DEVNULL,
        )
        for host in config.hosts
    ]

    outputs = await asyncio.gather(
        *(
            process.communicate(stdin.encode("utf-8") if stdin else None)
            for process, stdin in zip(processes, stdins or [None for _ in config.hosts])
        )
    )

    stdouts = [stdout.decode("utf-8").strip() for stdout, _ in outputs]
    stderrs = [stderr.decode("utf-8").strip() for _, stderr in outputs]

    def filter(
        objs: Iterable[Any], pred: Callable[[asyncio.subprocess.Process], bool]
    ) -> Iterable[Any]:
        return [obj for process, obj in zip(processes, objs) if pred(process)]

    def succeeded(objs: Iterable[Any]) -> Iterable[Any]:
        return filter(objs, lambda process: process.returncode == 0)

    def failed(objs: Iterable[Any]) -> Iterable[Any]:
        return filter(objs, lambda process: process.returncode != 0)

    for host, stderr in failed(zip(config.hosts, stderrs)):
        message = f"Failed connecting over SSH to {host.hostname} ({stderr})"

        if config.throw_on_error:
            raise RuntimeError(message)
        elif not config.quiet:
            print(message, file=sys.stderr)

    hosts = succeeded(config.hosts)
    stdouts = succeeded(stdouts)
    stderrs = succeeded(stderrs)

    reprint([host.hostname for host in hosts], stderrs, file=sys.stderr)

    return hosts, stdouts
