from contextlib import contextmanager
import subprocess
from typing import Iterable

from genv.devices.device import Device
from genv.devices.snapshot import Snapshot
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
