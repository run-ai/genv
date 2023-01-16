from dataclasses import dataclass
import subprocess
from typing import Dict, Iterable, Optional, Any, Mapping, Collection

from genv import nvidia_smi
from genv.serialization.partial_deserialization import smart_ctor
from genv.runners import Runner


# NOTE(raz): This should be the layer that queries and controls the state of Genv regarding devices.
# Currently, it relies on executing the device manager executable of Genv, as this is where the logic is implemented.
# This however should be done oppositely.
# The entire logic that queries and controls devices.json should be implemented here, and the device manager executable
# should use methods from here.
# It should take the Genv lock for the atomicity of the transaction, and print output as needed.
# The current architecture has an inherent potential deadlock because each manager locks a different lock, and might
# call the other manager.



@dataclass
class Device:

    @dataclass
    class Usage:
        """
        The GPU utilization and amount of GPU memory consumed of the device.
        """

        used_memory: str
        gpu_utilization: float
        memory_utilization: float

        def __init__(self, *args_dict, **kwargs):
            smart_ctor(self, *args_dict, **kwargs)

    index: int
    total_memory: Optional[str] = None
    eids: Optional[Iterable[str]] = None
    gpu_uuid: Optional[str] = None
    usage: Optional[Usage] = None

    def __init__(self, *args_dict, **kwargs):
        smart_ctor(self, *args_dict, **kwargs)

    @staticmethod
    def monitoring_data_keys() -> Collection[str]:
        return ["gpu_index", "gpu_uuid", "total_memory", "used_memory", "gpu_utilization", "memory_utilization"]

    def get_monitoring_data(self, add_genv_data: bool = False) -> Dict[str, Any]:
        monitoring_data = dict()
        monitoring_data["gpu_index"] = self.index
        monitoring_data["gpu_uuid"] = self.gpu_uuid
        monitoring_data["total_memory"] = self.total_memory
        monitoring_data["used_memory"] = self.usage.used_memory
        monitoring_data["gpu_utilization"] = self.usage.gpu_utilization
        monitoring_data["memory_utilization"] = self.usage.memory_utilization
        return monitoring_data


def snapshot() -> Iterable[Device]:
    return [Device(index, eids=d["eids"]) for index, d in ps().items()]


async def nvidia_smi_snapshot(host_runner: Runner) -> Iterable[Device]:
    """
    Get the list of GPU devices data using nvidia-smi only (do not assume that genv is installed).
    :param host_runner: host process runner abstraction
    :return: List of the machine GPU devices
    """
    devices_dict_lst = await nvidia_smi.get_devices_metric_data(host_runner)

    devices_lst = []
    for dev_dict in devices_dict_lst:
        device_obj = Device(index=dev_dict['index'],
                            gpu_uuid=dev_dict['gpu_uuid'],
                            total_memory=dev_dict['memory_total'],
                            usage=Device.Usage(used_memory=dev_dict['memory_used'],
                                               gpu_utilization=float(dev_dict['gpu_utilization']),
                                               memory_utilization=float(dev_dict['memory_utilization']))
                            )
        devices_lst.append(device_obj)

    return devices_lst


def ps() -> Dict[int, Iterable[str]]:
    """
    Returns information about device and active attachments.

    :return: A mapping between device index and all attached environment identifiers
    """
    devices = dict()

    for line in (
        subprocess.check_output(
            "genv exec devices ps --no-header --format csv", shell=True
        )
        .decode("utf-8")
        .strip()
        .splitlines()
    ):
        index, eid, _, _ = line.split(",")
        index = int(index)

        if index not in devices:
            devices[index] = {"eids": []}

        if eid:
            devices[index]["eids"].append(eid)

    return devices


def detach(eid: str, index: int) -> None:
    """
    Detaches an environment from a device.

    :param eid: Environment identifier
    :param index: Device index
    :return: None
    """
    # TODO(raz): support detaching from multiple devices at the same time
    subprocess.check_call(
        f"genv exec devices detach --quiet --eid {eid} --index {index}", shell=True
    )
