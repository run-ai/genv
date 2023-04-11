import os
from typing import Dict, Iterable, Optional

from .device_info import DeviceInfo
from .app_info import AppInfo
from ..runners import Runner, LocalRunner

DEFAULT_NVIDIA_SMI_ENV_VARS = {"GENV_BYPASS": "1", **os.environ}
DEFAULT_LOCAL_RUNNER = LocalRunner(DEFAULT_NVIDIA_SMI_ENV_VARS)

NVIDIA_SMI = "nvidia-smi"
CSV_FORMAT_PARAM = "--format=csv,noheader,nounits"
NVIDIA_CSV_SPLITTER = ", "


async def nvidia_devices(runner: Optional[Runner] = None) -> Dict[str, DeviceInfo]:
    """
    Queries device UUIDs.

    :return: A mapping from device UUID to its index
    """
    if runner is None:
        runner = DEFAULT_LOCAL_RUNNER

    stdout = (
        await runner.run(
            NVIDIA_SMI, "--query-gpu=uuid,index,utilization.gpu,memory.used,utilization.memory",
            CSV_FORMAT_PARAM,
            check=True
        )
    ).stdout

    mapping = dict()

    for line in stdout.splitlines():
        uuid, index, utilization, used_memory, memory_utilization = line.split(NVIDIA_CSV_SPLITTER)
        dev_info = DeviceInfo(uuid, int(index), int(utilization), used_memory, int(memory_utilization))
        mapping[uuid] = dev_info

    return mapping


async def compute_apps(runner: Optional[Runner] = None) -> Iterable[AppInfo]:
    """
    Queries the running compute apps.
    """
    if runner is None:
        runner = DEFAULT_LOCAL_RUNNER

    output = (
        await runner.run(
            NVIDIA_SMI,
            "--query-compute-apps=gpu_uuid,pid,used_gpu_memory",
            CSV_FORMAT_PARAM,
            check=True)
    ).stdout

    apps = []

    for line in output.splitlines():
        gpu_uuid, pid, used_gpu_memory = line.split(NVIDIA_CSV_SPLITTER)
        apps.append(AppInfo(int(pid), gpu_uuid, used_gpu_memory))

    return apps
