import asyncio
import os
from asyncio.subprocess import Process
from typing import Dict, Optional, List, Tuple

from .runner import Runner as Base


class Runner(Base):
    host_name: str
    timeout: Optional[int]
    __SSH_COMMAND_PREFIX = "ssh"
    __SSH_TIMEOUT_PARAMETER = "-o ConnectTimeout={0}"

    def __init__(self, host_name: str, timeout: Optional[int] = None, process_env: Optional[Dict] = None):
        super().__init__(process_env)
        self.host_name = host_name
        self.timeout = timeout

    def name(self) -> str:
        return self.host_name

    async def _open_process(self, *args: str, stdin_fd: int, sudo: bool) -> Process:
        ssh_parameters = self.calc_ssh_params()
        remote_command = self.calc_command_on_remote_machine(args, sudo)

        return await asyncio.create_subprocess_exec(
            Runner.__SSH_COMMAND_PREFIX,
            *ssh_parameters,
            remote_command,
            stdin=stdin_fd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

    def calc_ssh_params(self) -> List[str]:
        ssh_parameters = []
        if self.timeout is not None:
            ssh_parameters.append(self.__SSH_TIMEOUT_PARAMETER.format(self.timeout))
        ssh_parameters.append(self.host_name)
        return ssh_parameters

    def calc_command_on_remote_machine(self, args: Tuple[str, ...], sudo: bool) -> str:
        command = " ".join(args)
        if self._process_env:
            command = self._add_environment_vars(command, self._process_env)
        if sudo:
            command = f"sudo {command}"
        return command

    def _get_error_msg(self, command: str, stderr: str):
        return f"Failed to run a command using ssh on {self.host_name}: command: '{command}' ({stderr})"

    @staticmethod
    def _add_environment_vars(command: str, process_env: Dict[str, str]):
        env_str = " ".join([f'{var_key}={var_value}' for var_key, var_value in process_env.items()])
        command = f'env {env_str} {command}'
        return command

    @staticmethod
    def calc_remote_path_env(root: str) -> str:
        path_env = f"$PATH:{root}/bin"

        if os.path.realpath(os.path.join(os.environ["GENV_ROOT"], "devel/shims")) in [
            os.path.realpath(path) for path in os.environ["PATH"].split(":")
        ]:
            path_env = f"{path_env}:{root}/devel/shims"

        return path_env
