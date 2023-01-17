from typing import Dict, Iterable

from genv.runners import Runner


async def device_uuids(host_runner: Runner) -> Dict[str, int]:
    """
    Queries device UUIDs.

    :return: A mapping from device UUID to its index
    """
    output = await host_runner.run("nvidia-smi", "--query-gpu=uuid,index", "--format=csv,noheader")

    mapping = dict()

    for line in output.splitlines():
        uuid, index = line.split(", ")
        mapping[uuid] = int(index)

    return mapping


async def compute_apps(host_runner: Runner) -> Iterable[Dict]:
    """
    Queries the running compute apps.
    """
    output = await host_runner.run(
        "nvidia-smi",
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


async def get_devices_metric_data(host_runner: Runner) -> Iterable[Dict]:
    """
    Query GPU devices metric data via nvidia-smi
    :param host_runner: host process runner abstraction
    :return: A list of dictionaries, each representing a single device and it's metrics
    """
    output = await host_runner.run(
        "nvidia-smi",
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
