import asyncio
from abc import ABC, abstractmethod
from asyncio.subprocess import Process
from typing import Dict, Optional


class CommandResults:
    process: Process
    stdout: str
    stderr: str

    def __init__(self, process: Process, stdout: str, stderr: str):
        self.process = process
        self.stdout = stdout
        self.stderr = stderr


class Runner(ABC):
    _process_env: Dict[str, str]

    def __init__(self, process_env: Optional[Dict] = None):
        self._process_env = process_env

    async def run(
        self,
        *args: str,
        stdin: Optional[str] = None,
        sudo: bool = False,
        check: bool = False,
    ) -> CommandResults:
        stdin_fd = asyncio.subprocess.PIPE if stdin else asyncio.subprocess.DEVNULL
        process = await self._open_process(*args, stdin_fd=stdin_fd, sudo=sudo)

        stdout, stderr = await process.communicate(
            stdin.encode("utf-8") if stdin else None
        )

        stdout = stdout.decode("utf-8").strip()
        stderr = stderr.decode("utf-8").strip()

        if check and process.returncode != 0:
            command = " ".join(args)
            stdin_str = " with stdin " + str(stdin)
            raise RuntimeError(
                f"Failed running '{command}' {' with sudo ' if sudo else ''} { stdin_str if stdin else '' } ({stderr})"
            )

        return CommandResults(process, stdout, stderr)

    @abstractmethod
    async def _open_process(self, *args: str, stdin_fd: int, sudo: bool) -> Process:
        raise NotImplementedError("This should be implemented in subclasses")
