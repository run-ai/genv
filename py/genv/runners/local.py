import asyncio
from asyncio.subprocess import Process

from .runner import Runner


class LocalRunner(Runner):
    def name(self) -> str:
        return "local"

    async def _execute(self, *args, process_env, sudo: bool = False) -> Process:
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
        return f"Failed to run a command on the local machine: command: '{command}' ({stderr})"
