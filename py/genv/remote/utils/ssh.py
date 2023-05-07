import asyncio
from dataclasses import dataclass
import sys
from typing import Any, Callable, Iterable, Optional, Tuple

from genv.utils.runners import SSH as Runner

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
    ssh_runners_and_inputs = []
    for host, stdin in zip(config.hosts, stdins or [None for _ in config.hosts]):
        ssh_runner = Runner(
            host.hostname,
            host.timeout,
            {"PATH": Runner.calc_remote_path_env(host.root)},
        )
        ssh_runners_and_inputs.append((ssh_runner, stdin))

    ssh_outputs = await asyncio.gather(
        *(
            ssh_runner.run("genv", *command.args, stdin=stdin, sudo=command.sudo)
            for ssh_runner, stdin in ssh_runners_and_inputs
        )
    )

    processes = [runner_output.command_process for runner_output in ssh_outputs]
    stdouts = [runner_output.stdout for runner_output in ssh_outputs]
    stderrs = [runner_output.stderr for runner_output in ssh_outputs]

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
