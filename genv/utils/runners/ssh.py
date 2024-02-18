import asyncio
from asyncio.subprocess import Process
from typing import Dict, Optional

from .runner import Runner as Base


class Runner(Base):
    hostname: str
    username: Optional[str]
    timeout: Optional[int]

    def __init__(
        self,
        hostname: str,
        username: Optional[str] = None,
        timeout: Optional[int] = None,
        process_env: Optional[Dict[str, str]] = None,
    ):
        super().__init__(process_env)
        self.hostname = hostname
        self.username = username
        self.timeout = timeout

    async def _open_process(self, *args: str, stdin_fd: int, sudo: bool) -> Process:
        ssh_parameters = []

        if self.username:
            ssh_parameters.extend(["-l", self.username])

        if self.timeout is not None:
            ssh_parameters.extend(["-o", f"ConnectTimeout={self.timeout}"])

        remote_command = " ".join(args)

        if self._process_env:
            remote_command = (
                "env "
                + " ".join(
                    [f"{name}={value}" for name, value in self._process_env.items()]
                )
                + " "
                + remote_command
            )

        if sudo:
            remote_command = f"sudo {remote_command}"

        return await asyncio.create_subprocess_exec(
            "ssh",
            *ssh_parameters,
            self.hostname,
            remote_command,
            stdin=stdin_fd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
