from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
import subprocess
from typing import Callable, Iterable, Optional, Union

from genv.os_ import access_lock, create_lock
from genv.utils import get_temp_file_path, memory_to_bytes, DATETIME_FMT

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
    class Attachement:
        eid: str
        gpu_memory: Optional[str]
        time: str

    index: int
    total_memory: str
    attachments: Iterable[Attachement]

    @property
    def eids(self) -> Iterable[str]:
        return [attachment.eid for attachment in self.attachments]

    @property
    def attached(self) -> bool:
        return len(self.eids) > 0

    @property
    def detached(self) -> bool:
        return len(self.eids) == 0

    @property
    def total_memory_bytes(self) -> int:
        """
        Returns the device total memory in bytes.
        """
        return memory_to_bytes(self.total_memory)

    @property
    def available_memory_bytes(self) -> int:
        """
        Returns the device available memory in bytes.
        """
        available_bytes = memory_to_bytes(self.total_memory)

        for attachment in self.attachments:
            available_bytes -= memory_to_bytes(
                attachment.gpu_memory or self.total_memory
            )

        return max(available_bytes, 0)

    def available(self, gpu_memory: Optional[str]) -> bool:
        """
        Returns is the device is available with respect to the given memory specification.
        If memory is specified, checks if this amount is available.
        Otherwise, checks if the device is detached.
        """
        if gpu_memory is None:
            return self.detached

        return self.available_memory_bytes >= memory_to_bytes(gpu_memory)

    def filter(self, *, eids: Iterable[str]):
        """
        Returns a new device with only the given environment identifiers.
        """
        return Device(
            self.index,
            self.total_memory,
            [attachment for attachment in self.attachments if attachment.eid in eids],
        )

    def attach(self, eid: str, gpu_memory: Optional[str], time: str) -> None:
        """
        Attaches an environment.
        """
        self.attachments.append(Device.Attachement(eid, gpu_memory, time))

    def detach(self, eid: str) -> None:
        """
        Detaches an environment.
        """
        for index, attachment in enumerate(self.attachments):
            if attachment.eid == eid:
                del self.attachments[index]


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
        not_indices: Optional[Iterable[int]] = None,
        eid: Optional[str] = None,
        eids: Optional[Iterable[str]] = None,
        attached: Optional[bool] = None,
        function: Optional[Callable[[Device], bool]] = None,
    ):
        """
        Returns a new filtered snapshot.

        :param deep: Perform deep filtering
        :param indices: Device indices to keep
        :param not_indices: Device indices to remove
        :param eid: Environment identifier to keep
        :param eids: Environment identifiers to keep
        :param attached: Keep only devices with environments attached or not
        :param function: Keep devices on which the lambda returns True
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

        if not_indices is not None:
            devices = [device for device in devices if device.index not in not_indices]

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

        if function is not None:
            devices = [device for device in devices if function(device)]

        return Snapshot(devices)

    def attach(
        self, eid: str, indices: Union[Iterable[int], int], gpu_memory: Optional[str]
    ) -> None:
        """
        Attaches devices to an environment.
        """

        if isinstance(indices, int):
            indices = [indices]

        time = datetime.now().strftime(DATETIME_FMT)

        for index in indices:
            self.devices[index].attach(eid, gpu_memory, time)


def snapshot() -> Snapshot:
    """
    Returns a devices snapshot.
    """

    lines = (
        subprocess.check_output(
            "genv exec devices query --query index total_memory attachments", shell=True
        )
        .decode("utf-8")
        .strip()
        .splitlines()
    )

    def parse_attachment(s: str) -> Device.Attachement:
        eid, gpu_memory, time = s.split("+")

        return Device.Attachement(
            eid,
            gpu_memory or None,
            time.replace("_", " "),
        )

    def parse_device(s: str) -> Device:
        index, total_memory, attachments = s.split(",")

        return Device(
            int(index),
            total_memory,
            [parse_attachment(attachment) for attachment in attachments.split(" ")]
            if attachments
            else [],
        )

    return Snapshot([parse_device(line) for line in lines])


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
