import asyncio
import os
from asyncio.subprocess import Process
from typing import Dict, Optional, Iterable

from .runner import Runner


class SshRunner(Runner):
    host_name: str
    process_env: Dict[str, str]
    __SSH_COMMAND_PREFIX = "ssh"

    def __init__(self, host_name: str, process_env: Optional[Dict] = None):
        self.host_name = host_name
        self.process_env = process_env

    def name(self) -> str:
        return self.host_name

    async def _open_process(self, *args, stdin: bool = False, process_env: Optional[Dict[str, str]] = None,
                            sudo: bool = False) -> (Process, str):
        if not process_env:
            process_env = self.process_env

        command = f'{" ".join(args)}'

        if process_env:
            command = await self.add_environment_vars(command)
        if sudo:
            command = f"sudo {command}"

        return await asyncio.create_subprocess_exec(
            SshRunner.__SSH_COMMAND_PREFIX,
            self.host_name,
            command,
            stdin=asyncio.subprocess.PIPE if stdin else asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

    async def add_environment_vars(self, command):
        env_str = ";".join([f'{var_key}={var_value}' for var_key, var_value in self.process_env.items()])
        command = f'env {env_str} {command}'
        return command

    async def _get_error_msg(self, command: str, stderr: str):
        return f"Failed to run a command using ssh on {self.host_name}: command: '{command}' ({stderr})"

    @staticmethod
    async def calc_remote_path_env(root: str) -> str:
        path_env = f"$PATH:{root}/bin"

        if os.path.realpath(os.path.join(os.environ["GENV_ROOT"], "devel/shims")) in [
            os.path.realpath(path) for path in os.environ["PATH"].split(":")
        ]:
            path_env = f"{path_env}:{root}/devel/shims"

        return path_env


async def run_on_hosts_ssh(hosts: Iterable[str], *args, process_env: Optional[Dict] = None, sudo: bool = False
                           ) -> Iterable[str]:
    hosts_runners = [SshRunner(host, process_env=process_env) for host in hosts]
    async_calls = [ssh_runner.run(*args, sudo=sudo) for ssh_runner in hosts_runners]
    return await asyncio.gather(*async_calls)
