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
    :param username: SSH login name
    :param timeout: SSH connection timeout
    """

    hostname: str
    username: Optional[str]
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
    :param shell: Run command as regular shell command
    """

    args: Iterable[str]
    sudo: bool = False
    shell: bool = False

    @property
    def all_args(self) -> Iterable[str]:
        """Returns all command arguments"""

        return self.args if self.shell else ["genv"] + self.args


async def run(
    config: Config,
    command: Command,
    stdins: Optional[Iterable[str]] = None,
) -> Tuple[Iterable[Host], Iterable[str]]:
    """
    Runs a command on multiple hosts over SSH.
    Waits for the command to finish on all hosts.
    Raises 'RuntimeError' if failed to connect to any of the hosts and 'config.throw_on_error' is True.

    :param config: Execution configuration
    :param command: Command specification
    :param stdins: Input to send per host

    :return: Returns the hosts that succeeded and their standard outputs
    """

    runners = [Runner(host.hostname, host.username, host.timeout) for host in config.hosts]

    results = await asyncio.gather(
        *(
            runner.run(*command.all_args, stdin=stdin, sudo=command.sudo, check=False)
            for runner, stdin in zip(runners, stdins or [None for _ in runners])
        )
    )

    processes = [result.process for result in results]
    stdouts = [result.stdout for result in results]
    stderrs = [result.stderr for result in results]

    def filter(
        objs: Iterable[Any], pred: Callable[[asyncio.subprocess.Process], bool]
    ) -> Iterable[Any]:
        return [obj for process, obj in zip(processes, objs) if pred(process)]

    def succeeded(objs: Iterable[Any]) -> Iterable[Any]:
        return filter(objs, lambda process: process.returncode == 0)

    def failed(objs: Iterable[Any]) -> Iterable[Any]:
        return filter(objs, lambda process: process.returncode != 0)

    for host, stderr in failed(zip(config.hosts, stderrs)):
        message = f"Failed running SSH command on {host.hostname} ({stderr})"

        if config.throw_on_error:
            raise RuntimeError(message)
        elif not config.quiet:
            print(message, file=sys.stderr)

    hosts = succeeded(config.hosts)
    stdouts = succeeded(stdouts)
    stderrs = succeeded(stderrs)

    reprint([host.hostname for host in hosts], stderrs, file=sys.stderr)

    return hosts, stdouts
