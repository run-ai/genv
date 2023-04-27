from contextlib import contextmanager
import os
from typing import Iterable

import genv.devices


def attached() -> Iterable[int]:
    """
    Returns the attached device indices.
    Raises RuntimeError if not running in an active environment.
    """

    indices = os.environ.get("CUDA_VISIBLE_DEVICES")

    if indices is None:
        raise RuntimeError("Not running in an active environment")

    if indices == "-1":
        return []

    return [int(index) for index in indices.split(",")]


@contextmanager
def lock() -> None:
    """
    Obtains exclusive access to the attached device.
    """

    indices = attached()

    if len(indices) == 0:
        raise RuntimeError("Environment is detached from devices")

    if len(indices) > 1:
        raise RuntimeError("Environment is attached to more than a single device")

    index = indices[0]

    with genv.devices.lock(index):
        yield
