import os
from typing import Dict, Iterable

from .runners import Runner, Local

DEFAULT_NVIDIA_SMI_ENV_VARS = {"GENV_BYPASS": "1", **os.environ}
DEFAULT_LOCAL_RUNNER = Local(DEFAULT_NVIDIA_SMI_ENV_VARS)

NVIDIA_SMI = "nvidia-smi"
CSV_FORMAT_PARAM = "--format=csv,noheader,nounits"
NVIDIA_CSV_SPLITTER = ", "


async def device_uuids(runner: Runner = DEFAULT_LOCAL_RUNNER) -> Dict[str, int]:
    """
    Queries device UUIDs.

    :return: A mapping from device UUID to its index
    """
    stdout = (await runner.run(NVIDIA_SMI, "--query-gpu=uuid,index", CSV_FORMAT_PARAM, check=True)).stdout

    mapping = dict()

    for line in stdout.splitlines():
        uuid, index = line.split(NVIDIA_CSV_SPLITTER)
        mapping[uuid] = int(index)

    return mapping


async def compute_apps(runner: Runner = DEFAULT_LOCAL_RUNNER) -> Iterable[Dict]:
    """
    Queries the running compute apps.
    """
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

        apps.append(
            dict(
                gpu_uuid=gpu_uuid, pid=int(pid), used_gpu_memory=f"{used_gpu_memory}mi"
            )
        )

    return apps
