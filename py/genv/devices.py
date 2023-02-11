from dataclasses import dataclass
import subprocess
from typing import Dict, Iterable, Optional


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
    index: int
    eids: Iterable[str]

    def filter(self, eids: Iterable[str]):
        """
        Returns a new device with only the given environment identifiers.
        """
        return Device(self.index, [eid for eid in eids if eid in self.eids])


@dataclass
class Snapshot:
    """
    A snapshot of devices.
    """

    devices: Iterable[Device]

    def __iter__(self):
        return self.devices.__iter__()

    def __len__(self):
        return self.devices.__len__()

    def filter(
        self, *, eids: Optional[Iterable[str]] = None, attached: Optional[bool] = None
    ):
        """
        Returns a new filtered snapshot.

        :param eids: Environment identifiers to keep
        :param attached: Keep only devices with environments attached or not
        """

        devices = self.devices

        if eids is not None:
            devices = [device.filter(eids) for device in devices]

        if attached is not None:
            pred = (lambda envs: envs > 0) if attached else (lambda envs: envs == 0)

            devices = [device for device in devices if pred(len(device.eids))]

        return Snapshot(devices)


def snapshot() -> Snapshot:
    return Snapshot([Device(index, d["eids"]) for index, d in ps().items()])


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