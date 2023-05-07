from contextlib import contextmanager
import subprocess
from typing import Any, Iterable, Union

import genv.utils
from genv.entities import Device, Devices
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


def snapshot() -> Devices:
    """
    Returns an environments snapshot.
    """
    return State().load()


def attach(eid: str) -> Iterable[int]:
    """
    Attaches an environment to devices.
    The device count is taken from the environment configuration.
    Does not detach devices if already attached to more devices.

    :return: Attached device indices
    """
    with State() as devices:
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
    with State() as devices:
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
