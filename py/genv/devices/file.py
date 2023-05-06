from contextlib import contextmanager
import subprocess
from typing import Any, Iterable, Union

import genv.utils
from genv.entities.devices import Device, Devices
import genv.serialization
import genv.envs


_PATH = genv.utils.get_temp_file_path("devices.json")


def _get_devices_total_memory() -> Iterable[str]:
    """
    Gets total memory of all devices as string using nvidia-smi.
    """

    # move to genv.nvidia_smi once async is supported here
    return [
        f"{int(line)}mi"
        for line in subprocess.check_output(
            "GENV_BYPASS=1 nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits",
            shell=True,
        ).splitlines()
    ]


def _creator() -> Devices:
    """
    Creates an empty state.
    """

    return Devices(
        [
            Device(index, total_memory, [])
            for index, total_memory in enumerate(_get_devices_total_memory())
        ]
    )


def _converter(o: Union[Devices, Any]) -> Devices:
    """
    Converts the loaded object if needed.
    """

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


def _cleaner(devices: Devices) -> None:
    """
    Cleans up device attachments from inactive environments.
    """

    envs = genv.envs.snapshot()

    devices.cleanup(poll_eid=lambda eid: eid in envs.eids)


def load(cleanup: bool = True, reset: bool = False) -> Devices:
    """
    Loads from disk.
    """
    return genv.utils.load_state(
        _PATH,
        creator=_creator,
        cleaner=_cleaner,
        converter=_converter,
        json_decoder=genv.serialization.JSONDecoder,
        cleanup=cleanup,
        reset=reset,
    )


def save(devices: Devices) -> None:
    """
    Saves to disk.
    """
    genv.utils.save_state(
        devices,
        _PATH,
        json_encoder=genv.serialization.JSONEncoder,
    )


@contextmanager
def mutate(cleanup: bool = True, reset: bool = False) -> Devices:
    """
    Mutates state on disk.
    """
    devices = load(cleanup, reset)

    yield devices

    save(devices)
