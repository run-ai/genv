import asyncio
from asyncio.subprocess import Process

from .runner import Runner as Base


class Runner(Base):
    async def _open_process(self, *args: str, stdin_fd: int, sudo: bool) -> Process:
        if sudo:
            args = ["sudo", *args]

        return await asyncio.create_subprocess_exec(
            *args,
            env=self._process_env,
            stdin=stdin_fd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
