from contextlib import contextmanager
from glob import glob
import os
import re
from typing import Iterable, Optional

import genv.utils
import genv.core.devices

import genv.sdk.env


def visible() -> Optional[Iterable[int]]:
    """
    Returns the indices of visible devices if set.
    """

    indices = os.environ.get("CUDA_VISIBLE_DEVICES")

    if indices is None:
        return None

    if indices == "-1":
        return []

    return [int(index) for index in indices.split(",")]


def lockable() -> Iterable[int]:
    """
    Returns the indices of devices that have an existing lock.
    """

    dir = genv.utils.get_temp_file_path("devices")

    return [
        int(re.sub(r".*?(\d+)\.lock", r"\1", path)) for path in glob(f"{dir}/*.lock")
    ]


@contextmanager
def lock() -> None:
    """
    Obtains exclusive access to the attached devices.
    Does nothing if not running in an active environment or not attached to devices.
    """

    if not genv.sdk.env.active():
        yield
    else:
        if "GENV_SHELL" in os.environ:
            indices = visible()
        elif "GENV_CONTAINER" in os.environ:
            indices = lockable()
        else:
            raise RuntimeError("Failed to find device indices to lock")

        with genv.core.devices.lock(indices):
            yield
