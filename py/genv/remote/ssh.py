import asyncio
import sys
from typing import Iterable, Optional

from .utils import reprint


async def start(
    host: str, root: str, stdin: int, *args: str, sudo: bool = False, genv_command: bool = True
) -> asyncio.subprocess.Process:
    """
    Starts a background process that runs a Genv command on a remote host over SSH.

    :param host: Hostname or IP address
    :param root: Genv installation root directory
    :param stdin: Standard input
    :param args: Genv command line to run
    :param sudo: Run command as root using sudo

    :return: Returns the SSH process
    """
    if genv_command:
        command = f'env PATH="{root}/bin:$PATH" genv {" ".join(args)}'
    else:
        command = f'{" ".join(args)}'

    if sudo:
        command = f"sudo {command}"

    return await asyncio.create_subprocess_exec(
        "ssh",
        host,
        command,
        stdin=stdin,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )


async def run(
    hosts: Iterable[str],
    root: str,
    *args: str,
    stdins: Optional[Iterable[str]] = None,
    sudo: bool = False,
) -> Iterable[str]:
    """
    Runs a Genv command on multiple hosts over SSH.
    Waits for the command to finish successfully on all hosts.
    Raises 'RuntimeError' if failed to connect to any of the hosts.

    :param hosts: Hostnames or IP addresses
    :param root: Genv installation root directory
    :param args: Genv command line to run
    :param stdins: Stdins to send
    :param sudo: Run command with sudo

    :return: Returns the stdout from all hosts
    """
    processes = [
        await start(
            host,
            root,
            asyncio.subprocess.PIPE if stdins else asyncio.subprocess.DEVNULL,
            *args,
            sudo=sudo,
        )
        for host in hosts
    ]

    outputs = await asyncio.gather(
        *(
            process.communicate(stdin.encode("utf-8") if stdin else None)
            for process, stdin in zip(processes, stdins or [None for _ in hosts])
        )
    )

    stdouts = [stdout.decode("utf-8").strip() for stdout, _ in outputs]
    stderrs = [stderr.decode("utf-8").strip() for _, stderr in outputs]

    for host, process, stderr in zip(hosts, processes, stderrs):
        if process.returncode != 0:
            raise RuntimeError(f"Failed connecting over SSH to {host} ({stderr})")

    reprint(hosts, stderrs, file=sys.stderr)

    return stdouts
