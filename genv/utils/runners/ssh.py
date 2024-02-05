import asyncio
from asyncio.subprocess import Process
from typing import Dict, Optional, List, Tuple

from .runner import Runner as Base


class Runner(Base):
    host_name: str
    timeout: Optional[int]

    def __init__(
        self,
        host_name: str,
        timeout: Optional[int] = None,
        process_env: Optional[Dict] = None,
    ):
        super().__init__(process_env)
        self.host_name = host_name
        self.timeout = timeout

    async def _open_process(self, *args: str, stdin_fd: int, sudo: bool) -> Process:
        ssh_parameters = self.calc_ssh_params()
        remote_command = self.calc_command_on_remote_machine(args, sudo)

        return await asyncio.create_subprocess_exec(
            "ssh",
            *ssh_parameters,
            remote_command,
            stdin=stdin_fd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

    def calc_ssh_params(self) -> List[str]:
        ssh_parameters = []
        if self.timeout is not None:
            ssh_parameters.append(f"-o ConnectTimeout={self.timeout}")
        ssh_parameters.append(self.host_name)
        return ssh_parameters

    def calc_command_on_remote_machine(self, args: Tuple[str, ...], sudo: bool) -> str:
        command = " ".join(args)
        if self._process_env:
            command = self._add_environment_vars(command, self._process_env)
        if sudo:
            command = f"sudo {command}"
        return command

    @staticmethod
    def _add_environment_vars(command: str, process_env: Dict[str, str]):
        env_str = " ".join(
            [f"{var_key}={var_value}" for var_key, var_value in process_env.items()]
        )
        command = f"env {env_str} {command}"
        return command
