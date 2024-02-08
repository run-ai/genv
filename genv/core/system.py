import os
from genv.entities import System

from genv.utils.runners import Local


# TODO(raz): this should be combined with genv.remote.core.system()
async def system() -> System:
    """Returns information about the system"""

    GENV_COMMAND = "command -v genv 2> /dev/null || echo none"
    DEVICES_COMMAND = "nvidia-smi --query-gpu=index,utilization.gpu,temperature.gpu,memory.used,memory.total --format=csv,noheader,nounits"

    command = [
        "bash",
        "-c",
        f"({GENV_COMMAND}) && ({DEVICES_COMMAND})",  # NOTE(raz): when using a local runner we don't need to escape this argument
    ]

    runner = Local({"GENV_BYPASS": "1", **os.environ})
    stdout = (await runner.run(*command, check=True)).stdout

    genv_info, device_infos = stdout.split("\n", 1)

    def parse_genv_info(info: str) -> System.Genv:
        return System.Genv(installed=info != "none")

    def parse_device_info(line: str) -> System.Device:
        index, utilization, temperature, used_memory, total_memory = line.split(", ")

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
