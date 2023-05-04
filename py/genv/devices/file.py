import os
import subprocess
from typing import Any, Iterable, Union
from genv import json_, utils

from genv.devices.device import Device
from genv.devices.snapshot import Snapshot

PATH = utils.get_temp_file_path("devices.json")


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


def _convert(o: Union[Snapshot, Any]) -> Snapshot:
    """
    Converts the loaded state object to a snapshot if it not already is.
    """

    # the following logic converts state files from versions <= 0.8.0.
    # note that the indicator is 'o.devices' and not 'o' itself because the structure of
    # the state file from these versions was similar to the snapshot structure (a single
    # key named "devices") so the JSON decoder parsed the object as a snapshot object.
    if isinstance(o.devices, dict):
        o = Snapshot(
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


def load(reset: bool = False) -> Snapshot:
    """
    Loads from disk.
    """
    if os.path.exists(PATH) and not reset:
        return utils.load_state(
            PATH,
            convert=_convert,
            json_decoder=json_.JSONDecoder,
        )

    return Snapshot(
        [
            Device(index, total_memory, [])
            for index, total_memory in enumerate(_get_devices_total_memory())
        ]
    )


def save(snapshot: Snapshot) -> None:
    """
    Saves to disk.
    """
    utils.save_state(
        snapshot,
        PATH,
        json_encoder=json_.JSONEncoder,
    )
