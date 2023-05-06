from contextlib import contextmanager
import os
from typing import Iterable, Optional

import genv.core.devices


def attached() -> Optional[Iterable[int]]:
    """
    Returns the attached device indices or None if not running in an active environment.
    """

    indices = os.environ.get("CUDA_VISIBLE_DEVICES")

    if indices is None:
        return None

    if indices == "-1":
        return []

    return [int(index) for index in indices.split(",")]


@contextmanager
def lock() -> None:
    """
    Obtains exclusive access to the attached device.
    Does nothing ff not running in an active environment or not attached to devices.
    Raises RuntimeError if attached to more than a single device.
    """

    indices = attached()

    if indices is None or len(indices) == 0:
        yield
    else:
        if len(indices) > 1:
            raise RuntimeError("Environment is attached to more than a single device")

        with genv.core.devices.lock(index=indices[0]):
            yield
