from contextlib import contextmanager
from typing import Iterable

import genv.utils
from genv.entities import Devices

import genv.core.envs

from .file import load, mutate


def attach(eid: str) -> Iterable[int]:
    """
    Attaches an environment to devices.
    The device count is taken from the environment configuration.
    Does not detach devices if already attached to more devices.

    :return: Attached device indices
    """
    with mutate() as devices:
        envs = genv.core.envs.snapshot()
        env_config = envs[eid].config

        if env_config.gpus is not None:
            env_devices = devices.filter(eid=eid)

            diff = env_config.gpus - len(env_devices)

            if diff > 0:
                available_devices = devices.filter(
                    function=lambda device: device.available(env_config.gpu_memory)
                )

                if len(available_devices) < diff:
                    raise RuntimeError("No available devices")

                indices = available_devices.indices[:diff]

                devices.attach(eid, indices, env_config.gpu_memory)
            elif diff < 0:
                pass  # TODO(raz): support detaching devices if already attached to more

        return devices.filter(eid=eid).indices


def detach(eid: str, index: int) -> None:
    """
    Detaches an environment from a device.
    """
    with mutate() as devices:
        devices[index].detach(eid)


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
def lock(index: int) -> None:
    """
    Obtain exclusive access to a device.
    """
    path = get_lock_path(index)

    # NOTE(raz): currently, we wait on the lock even if it is already taken by our environment.
    # we should think if this is the desired behavior and if it's possible to lock once per environment.
    with genv.utils.access_lock(path):
        yield

    # TODO(raz): currently we wait for the entire device to become available.
    # we should support fractional usage and allow multiple environments to
    # access the device if the sum of their memory capacity fits.


def snapshot() -> Devices:
    """
    Returns an environments snapshot.
    """
    return load()
