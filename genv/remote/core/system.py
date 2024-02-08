from typing import Iterable, Tuple

from genv.entities import System

from ..utils import run, Host, Config, Command


async def system(config: Config) -> Tuple[Iterable[Host], Iterable[System]]:
    """Returns information about remote systems"""

    GENV_COMMAND = "command -v genv 2> /dev/null || echo none"
    DEVICES_COMMAND = "nvidia-smi --query-gpu=index,utilization.gpu,temperature.gpu,memory.used,memory.total --format=csv,noheader,nounits"

    command = Command(
        ["bash", "-c", f'"({GENV_COMMAND}) && ({DEVICES_COMMAND})"'], shell=True
    )

    hosts, stdouts = await run(config, command)

    def parse_stdout(stdout: str) -> System:
        genv_info, device_infos = stdout.split("\n", 1)

        def parse_genv_info(info: str) -> System.Genv:
            return System.Genv(installed=info != "none")

        def parse_device_info(line: str) -> System.Device:
            index, utilization, temperature, used_memory, total_memory = line.split(
                ", "
            )

            return System.Device(
                index=int(index),
                utilization=int(utilization),
                temperature=int(temperature),
                used_memory=f"{used_memory}mi",
                total_memory=f"{total_memory}mi",
            )

        return System(
            genv=parse_genv_info(genv_info),
            devices=[parse_device_info(line) for line in device_infos.splitlines()],
        )

    systems = [parse_stdout(stdout) for stdout in stdouts]

    return hosts, systems
