from contextlib import contextmanager
from dataclasses import dataclass
import subprocess
from typing import Iterable, Optional

from genv.os_ import access_lock, create_lock
from genv.utils import get_temp_file_path

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
    total_memory: str

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


def snapshot() -> Snapshot:
    """
    Returns a devices snapshot.
    """

    lines = (
        subprocess.check_output(
            "genv exec devices query --query index eids total_memory", shell=True
        )
        .decode("utf-8")
        .strip()
        .splitlines()
    )

    def convert(line: str) -> Device:
        index, eids, total_memory = line.split(",")

        return Device(int(index), eids.split(" ") if eids else [], total_memory)

    return Snapshot([convert(line) for line in lines])


def attach(eid: str) -> Iterable[int]:
    """
    Attaches an environment to devices.

    :param eid: Environment identifier
    :return: Attached device indices
    """
    output = (
        subprocess.check_output(
            f"genv exec devices attach --eid {eid}",
            shell=True,
        )
        .decode("utf-8")
        .strip()
    )

    return [int(index) for index in output.split(",") if index]


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


def get_lock_path(index: int, create: bool = False) -> str:
    """
    Returns the path of a device lock file.
    Creates the file if requested and it does not exist.
    """

    path = get_temp_file_path(f"devices/{index}.lock")

    if create:
        create_lock(path)

    return path


@contextmanager
def lock(index: int) -> None:
    """
    Obtain exclusive access to a device.
    """
    path = get_lock_path(index)

    # NOTE(raz): currently, we wait on the lock even if it is already taken by our environment.
    # we should think if this is the desired behavior and if it's possible to lock once per environment.
    with access_lock(path):
        yield

    # TODO(raz): currently we wait for the entire device to become available.
    # we should support fractional usage and allow multiple environments to
    # access the device if the sum of their memory capacity fits.
