from contextlib import ExitStack, contextmanager
import subprocess
from typing import Any, Iterable, Optional, Union

import genv.utils
from genv.entities import Device, Devices, Env
import genv.serialization

import genv.core.envs

from .utils import File


class State(File[Devices]):
    def __init__(self, cleanup: bool = True, reset: bool = False) -> None:
        super().__init__(
            genv.utils.get_temp_file_path("devices.json"),
            cleanup,
            reset,
        )

    def _create(self):
        # move to genv.utils.nvidia_smi once async is supported here
        devices_total_memory = [
            f"{int(line)}mi"
            for line in subprocess.check_output(
                "GENV_BYPASS=1 nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits",
                shell=True,
            ).splitlines()
        ]

        return Devices(
            [
                Device(index, total_memory, [])
                for index, total_memory in enumerate(devices_total_memory)
            ]
        )

    def _convert(self, o: Union[Any, Devices]) -> Devices:
        # the following logic converts state files from versions <= 0.8.0.
        # note that the indicator is 'o.devices' and not 'o' itself because the structure of
        # the state file from these versions was similar to the snapshot structure (a single
        # key named "devices") so the JSON decoder parsed the object as a snapshot object.
        if isinstance(o.devices, dict):
            o = Devices(
                [
                    Device(
                        int(index),
                        device["total_memory"],
                        [
                            Device.Attachement(
                                env["eid"],
                                env.get("gpu_memory", None),
                                env["attached"],
                            )
                            for env in device["eids"].values()
                        ],
                    )
                    for index, device in o.devices.items()
                ]
            )

        return o

    def _clean(self, devices: Devices) -> None:
        envs = genv.core.envs.snapshot()

        devices.cleanup(poll_eid=lambda eid: eid in envs.eids)


def cleanup() -> None:
    """Cleans up the state"""

    with State(cleanup=True):
        pass


def snapshot() -> Devices:
    """
    Returns an environments snapshot.
    """
    return State().load()


def attach(
    eid: str,
    *,
    index: Optional[int] = None,
    gpus: Optional[int] = None,
    gpu_memory: Optional[str] = None,
    allow_over_subscription: bool = False,
) -> Iterable[int]:
    """Attaches an environment to devices.

    Does not detach devices if already attached to more devices.

    :return: Attached device indices
    """
    if gpus is not None and index is not None:
        raise ValueError(
            'Can\'t use both "gpus" and "index" in genv.core.devices.attach()'
        )

    with State() as devices:
        env_devices = devices.filter(eid=eid)

        if index is not None:
            if index not in env_devices.indices:
                if not allow_over_subscription and not devices[index].available(
                    gpu_memory
                ):
                    raise RuntimeError(f"Device {index} is not available")

                devices.attach(eid, index, gpu_memory)
        elif gpus is not None:
            diff = gpus - len(env_devices)

            if diff > 0:
                not_env_devices = devices.filter(not_indices=env_devices.indices)

                indices = not_env_devices.find_available_devices(
                    diff, gpu_memory, allow_over_subscription
                )

                devices.attach(eid, indices, gpu_memory)
            elif diff < 0:
                pass  # TODO(raz): support detaching devices if already attached to more

        return devices.filter(eid=eid).indices


def detach(eid: str, index: Optional[int] = None) -> Iterable[int]:
    """
    Detaches an environment from a device.
    """
    with State() as devices:
        devices.detach(eid, index)

        return devices.filter(eid=eid).indices


def attached(eid: str) -> Iterable[int]:
    """Returns the indices of devices that are attached to an environment"""

    devices = snapshot()

    return devices.filter(eid=eid).indices


def get_lock_path(index: int, create: bool = False) -> str:
    """
    Returns the path of a device lock file.
    Creates the file if requested and it does not exist.
    """

    path = genv.utils.get_temp_file_path(f"devices/{index}.lock")

    if create:
        genv.utils.create_lock(path)

    return path


@contextmanager
def lock(indices: Union[Iterable[int], int]) -> None:
    """
    Obtain exclusive access to a device or a few devices.
    """
    if isinstance(indices, int):
        indices = [indices]

    # we sort here to decrease the chance of deadlock when different processes
    # try to lock the same devices in a different order.
    indices = sorted(indices)

    # NOTE(raz): currently, we wait on a lock even if it is already taken by our environment.
    # we should think if this is the desired behavior and if it's possible to lock once per environment.

    with ExitStack() as es:
        for index in indices:
            es.enter_context(genv.utils.access_lock(get_lock_path(index)))

        yield

    # TODO(raz): currently we wait for the entire device to become available.
    # we should support fractional usage and allow multiple environments to
    # access the device if the sum of their memory capacity fits.
