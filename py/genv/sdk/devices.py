from contextlib import contextmanager
from glob import glob
import os
import re
from typing import Iterable

import genv.utils
import genv.core

from . import env
from .utils import set_temp_env


def _visible() -> Iterable[int]:
    """Returns the indices of visible devices"""

    indices = os.environ["CUDA_VISIBLE_DEVICES"]

    return [] if indices == "-1" else [int(index) for index in indices.split(",")]


def _lockable() -> Iterable[int]:
    """Returns the indices of devices that have an existing lock"""

    dir = genv.utils.get_temp_file_path("devices")

    return [
        int(re.sub(r".*?(\d+)\.lock", r"\1", path)) for path in glob(f"{dir}/*.lock")
    ]


def _set_attached(indices: Iterable[int]) -> None:
    """Sets the device indices environment variables"""

    set_temp_env(
        "CUDA_VISIBLE_DEVICES", ",".join(map(str, indices)) if indices else "-1"
    )  # TODO(raz): support the case when this env var already exists

    # TODO(raz): should we set "CUDA_DEVICE_ORDER" as well?


def attach(allow_over_subscription: bool = False) -> Iterable[int]:
    """Attaches devices to the current environment.

    The device count is taken from the environment configuration.
    Does not detach devices if already attached to more devices.
    """

    if not env.active():
        raise RuntimeError("Not running in an active environment")

    config = env.configuration()

    with genv.utils.global_lock():
        indices = genv.core.devices.attach(
            env.eid(), config.gpus, config.gpu_memory, allow_over_subscription
        )

    _set_attached(indices)


def attached() -> Iterable[int]:
    """Returns the indices of attached devices.

    Indices are in host namespace even when running in a container.
    Raises RuntimeError if not running in an active environment.
    """

    if not env.active():
        raise RuntimeError("Not running in an active environment")

    # TODO(raz): replacing this logic with an explicit env var "GENV_DEVICE_INDICES"

    if "GENV_SHELL" in os.environ or "GENV_PYTHON" in os.environ:
        return _visible()
    elif "GENV_CONTAINER" in os.environ:
        return _lockable()

    raise RuntimeError("Failed to find attached device indices")


def load_attached() -> Iterable[int]:
    """Loads attached devices.

    Raises RuntimeError if not running in an active environment.
    """

    if not env.active():
        raise RuntimeError("Not running in an active environment")

    with genv.utils.global_lock():
        indices = genv.core.devices.attached(env.eid())

    _set_attached(indices)

    return indices


@contextmanager
def lock() -> None:
    """Obtains exclusive access to the attached devices.

    Does nothing if not running in an active environment or not attached to devices.
    """

    if not env.active():
        yield
    else:
        indices = attached()

        with genv.core.devices.lock(indices):
            yield
