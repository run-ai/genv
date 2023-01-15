import asyncio
from asyncio.subprocess import Process

from .runner import Runner


class SshRunner(Runner):
    host_name: str
    ssh_command_prefix = "ssh"

    def __init__(self, host_name: str):
        self.host_name = host_name

    async def _execute(self, *args, process_env, sudo: bool = False) -> Process:
        args = [SshRunner.ssh_command_prefix, *args]

        if sudo:
            args = ["sudo", *args]

        return await asyncio.create_subprocess_exec(
            *args,
            env=process_env,
            stdin=asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

    async def _get_error_msg(self, command: str, stderr: str):
        return f"Failed to run a command using ssh on {self.host_name}: command: '{command}' ({stderr})"
