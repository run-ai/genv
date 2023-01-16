import os
from abc import ABC, abstractmethod


class Runner(ABC):

    async def run(self, *args, sudo: bool = False):
        process = await self._execute(*args, sudo=sudo, process_env={"GENV_BYPASS": "1", **os.environ})

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            command = " ".join(args)
            raise RuntimeError(
                self._get_error_msg(command=command, stderr=stderr.decode('utf-8').strip())
            )

        return stdout.decode("utf-8").strip()

    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError('This should be implemented in subclasses')

    @abstractmethod
    async def _execute(self, *args, process_env, sudo: bool = False):
        pass

    @abstractmethod
    async def _get_error_msg(self, command: str, stderr: str):
        raise NotImplementedError('This should be implemented in subclasses')
