import asyncio
from abc import ABC, abstractmethod
from asyncio.subprocess import Process
from typing import Dict, Optional


class Runner(ABC):
    DEFAULT_STD_ENCODING = 'utf-8'
    _process_env: Dict[str, str]

    def __init__(self, process_env: Optional[Dict] = None):
        self._process_env = process_env

    # TODO: create class for return type
    async def run(self, *args: str, stdin: Optional[str] = None, sudo: bool = False):
        stdin_fd = asyncio.subprocess.PIPE if stdin else asyncio.subprocess.DEVNULL
        process = await self._open_process(*args,
                                           stdin_fd=stdin_fd,
                                           sudo=sudo)

        stdout, stderr = await process.communicate(stdin.encode(Runner.DEFAULT_STD_ENCODING) if stdin else None)
        stdout = stdout.decode(self.DEFAULT_STD_ENCODING).strip()
        stderr = stderr.decode(self.DEFAULT_STD_ENCODING).strip()

        return process, stdout, stderr

    async def run_to_success(self, *args: str, stdin: Optional[str] = None, sudo: bool = False) -> str:
        process, stdout, stderr = await self.run(*args, stdin=stdin, sudo=sudo)

        if process.returncode != 0:
            command = " ".join(args)
            raise RuntimeError(
                f"Failed running '{command}' ({stderr})"
            )
        else:
            return stdout

    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError('This should be implemented in subclasses')

    @abstractmethod
    async def _open_process(self, *args: str, stdin_fd: int, sudo: bool) -> Process:
        raise NotImplementedError('This should be implemented in subclasses')

    @abstractmethod
    def _get_error_msg(self, command: str, stderr: str):
        raise NotImplementedError('This should be implemented in subclasses')
