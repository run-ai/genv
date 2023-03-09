import asyncio
import os
from asyncio.subprocess import Process
from typing import Optional, Dict

from .runner import Runner


class LocalRunner(Runner):
    process_env: Dict[str, str]

    def __init__(self, process_env: Optional[Dict] = None):
        env_vars = os.environ.copy()
        if process_env:
            env_vars = env_vars.update(process_env)
        self.process_env = env_vars

    def name(self) -> str:
        return "local"

    async def _open_process(self, *args, stdin: bool = False, process_env: Optional[Dict[str, str]] = None,
                            sudo: bool = False) -> (Process, str):
        if not process_env:
            process_env = self.process_env

        if sudo:
            args = ["sudo", *args]

        return await asyncio.create_subprocess_exec(
            *args,
            env=process_env,
            stdin=asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        ), " ".join(args)

    async def _get_error_msg(self, command: str, stderr: str):
        return f"Failed to run a command on the local machine: command: '{command}' ({stderr})"
