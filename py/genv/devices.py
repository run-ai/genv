from dataclasses import dataclass
import subprocess
from typing import Dict, Iterable, Optional, List

import genv.nvidia_smi as nvidia_smi
from .snapshot_mode import SnapshotMode
from .runners import Runner


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
    class Status:
        utilization: int
        memory_used_bytes: str
        memory_utilization: int

    index: int
    eids: Iterable[str]
    status: Status

    @property
    def attached(self) -> bool:
        return len(self.eids) > 0

    @property
    def detached(self) -> bool:
        return len(self.eids) == 0

    def filter(self, *, eids: Iterable[str]):
        """
        Returns a new device with only the given environment identifiers.
        """
        return Device(self.index, [eid for eid in self.eids if eid in eids])


@dataclass
class Snapshot:
    """
    A snapshot of devices.
    """

    devices: Iterable[Device]

    @property
    def indices(self) -> Iterable[int]:
        return [device.index for device in self.devices]

    def __iter__(self):
        return self.devices.__iter__()

    def __len__(self):
        return self.devices.__len__()

    def __getitem__(self, index: int) -> Device:
        return next(device for device in self.devices if device.index == index)

    def filter(
        self,
        deep: bool = True,
        *,
        indices: Optional[Iterable[int]] = None,
        eid: Optional[str] = None,
        eids: Optional[Iterable[str]] = None,
        attached: Optional[bool] = None,
    ):
        """
        Returns a new filtered snapshot.

        :param deep: Perform deep filtering
        :param indices: Device indices to keep
        :param eid: Environment identifier to keep
        :param eids: Environment identifiers to keep
        :param attached: Keep only devices with environments attached or not
        """
        if eids:
            eids = set(eids)

        if eid:
            if not eids:
                eids = set()

            eids.add(eid)

        devices = self.devices

        if indices is not None:
            devices = [device for device in devices if device.index in indices]

        if eids is not None:
            if deep:
                devices = [device.filter(eids=eids) for device in devices]

            devices = [
                device
                for device in devices
                if any((eid in eids) for eid in device.eids)
            ]

        if attached is not None:
            if attached:
                devices = [device for device in devices if device.attached]
            else:
                devices = [device for device in devices if device.detached]

        return Snapshot(devices)


async def snapshot(mode: SnapshotMode = SnapshotMode.Full, runner: Optional[Runner] = None) -> Snapshot:
    nvidia_smi_info = await nvidia_smi.nvidia_devices(runner)

    devices = []
    if mode == SnapshotMode.Full:
        def get_matching_smi_info(device_index):
            return next(filter(lambda x: x.index == device_index, nvidia_smi_info.values()), None)

        for index, d in ps().items():
            smi_info = get_matching_smi_info(index)
            dev_status = Device.Status(smi_info.utilization, smi_info.used_memory_bytes, smi_info.memory_utilization)
            # TODO(david): fix json serialization so it will be able to handle internal objects
            device = Device(index, d["eids"], None)
            devices.append(device)
    else:
        for smi_info in nvidia_smi_info.values():
            dev_status = Device.Status(smi_info.utilization, smi_info.used_memory_bytes, smi_info.memory_utilization)
            device = Device(smi_info.index, [], dev_status)
            devices.append(device)
    return Snapshot(devices)


def ps() -> Dict[int, Dict[str, List[str]]]:
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
