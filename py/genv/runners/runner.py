from abc import ABC, abstractmethod
from asyncio.subprocess import Process
from typing import Dict, Optional


class Runner(ABC):
    DEFAULT_STD_ENCODING = 'utf-8'

    async def run(self, *args, stdin: Optional[str] = None, process_env: Optional[Dict[str, str]] = None,
                             sudo: bool = False):
        process, command = await self._open_process(*args, stdin=True, process_env=process_env, sudo=sudo)

        stdout, stderr = await process.communicate(stdin.encode(Runner.DEFAULT_STD_ENCODING) if stdin else None)
        stdout = stdout.decode("utf-8").strip()
        stderr = stderr.decode("utf-8").strip()

        return process, stdout, stderr, command

    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError('This should be implemented in subclasses')

    @abstractmethod
    async def _open_process(self, *args, stdin: bool = False, process_env: Optional[Dict[str, str]] = None,
                            sudo: bool = False) -> (Process, str):
        raise NotImplementedError('This should be implemented in subclasses')

    @abstractmethod
    async def _get_error_msg(self, command: str, stderr: str):
        raise NotImplementedError('This should be implemented in subclasses')
