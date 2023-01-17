import asyncio
import sys
from abc import ABC, abstractmethod
from asyncio.subprocess import Process
from typing import Dict, Optional, Iterable, List


class Runner(ABC):
    DEFAULT_STD_ENCODING = 'utf-8'

    async def run(self, *args, process_env: Optional[Dict[str, str]] = None, sudo: bool = False):
        stdout_in_lst = await self.run_with_stdin(*args, stdins=[""], process_env=process_env, sudo=sudo)
        return stdout_in_lst[0]

    async def run_with_stdin(self, *args, stdins: Iterable[str], process_env: Optional[Dict[str, str]] = None,
                  sudo: bool = False) -> List[str]:
        process, command = await self._open_process(*args, stdin=True, process_env=process_env, sudo=sudo)

        outputs = await asyncio.gather(
            *(
                process.communicate(stdin.encode(Runner.DEFAULT_STD_ENCODING) if stdin else None)
                for process, stdin in zip([process], stdins)
            )
        )

        stdouts = [stdout.decode(Runner.DEFAULT_STD_ENCODING).strip() for stdout, _ in outputs]
        stderrs = [stderr.decode(Runner.DEFAULT_STD_ENCODING).strip() for _, stderr in outputs]

        for stderr in stderrs:
            if process.returncode != 0:
                raise RuntimeError(await self._get_error_msg(command=command, stderr=stderr.decode('utf-8').strip()))
            elif stderr and len(stderr) > 0:
                print(f"{self.name()} call succeeded, but returned error: {stderr}", file=sys.stderr)

        return stdouts

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
