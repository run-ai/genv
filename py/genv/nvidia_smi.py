import asyncio
import os
from typing import Dict, Iterable


async def run(machine_name: str, *args: str) -> str:
    """
    Runs nvidia-smi with the given arguments as a subprocess, waits for it and returns its output.
    Raises 'RuntimeError' if subprocess exited with failure.
    """
    args = ["nvidia-smi", *args]

    if machine_name != "local":
        args.insert(0, "ssh")

    process = await asyncio.create_subprocess_exec(
        *args,
        env={"GENV_BYPASS": "1", **os.environ},
        stdin=asyncio.subprocess.DEVNULL,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        command = " ".join(args)
        raise RuntimeError(
            f"Failed running '{command}' ({stderr.decode('utf-8').strip()})"
        )

    return stdout.decode("utf-8").strip()


async def device_uuids() -> Dict[str, int]:
    """
    Queries device UUIDs.

    :return: A mapping from device UUID to its index
    """
    output = await run("local", "--query-gpu=uuid,index", "--format=csv,noheader")

    mapping = dict()

    for line in output.splitlines():
        uuid, index = line.split(", ")
        mapping[uuid] = int(index)

    return mapping


async def compute_apps() -> Iterable[Dict]:
    """
    Queries the running compute apps.
    """
    output = await run(
        "local",
        "--query-compute-apps=gpu_uuid,pid,used_gpu_memory",
        "--format=csv,noheader,nounits",
    )

    apps = []

    for line in output.splitlines():
        gpu_uuid, pid, used_gpu_memory = line.split(", ")

        apps.append(
            dict(
                gpu_uuid=gpu_uuid, pid=int(pid), used_gpu_memory=f"{used_gpu_memory}mi"
            )
        )

    return apps


async def get_devices_metric_data(machine_name: str = "local") -> Iterable[Dict]:
    """
    Query GPU devices metric data via nvidia-smi
    :return: A list of dictionaries, each representing a single device and it's metrics
    """
    output = await run(
        machine_name,
        "--query-gpu=index,uuid,timestamp,memory.used,memory.total,utilization.gpu,utilization.memory",
        "--format=csv,noheader,nounits"
    )

    devices = []

    for line in output.splitlines():
        index, gpu_uuid, timestamp, memory_used, memory_total, gpu_utilization, memory_utilization = line.split(", ")

        devices.append(
            dict(
                index=index, gpu_uuid=gpu_uuid, timestamp=timestamp,
                memory_used=f"{memory_used}mi", memory_total=f"{memory_total}mi",
                gpu_utilization=gpu_utilization, memory_utilization=memory_utilization
            )
        )

    return devices
