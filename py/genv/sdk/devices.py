from contextlib import contextmanager
from glob import glob
import os
import re
from typing import Iterable, Optional

import genv.utils
import genv.core

from . import env
from .utils import set_temp_env_var


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


def _update_env(indices: Iterable[int]) -> None:
    """Updates the device indices environment variables"""

    set_temp_env_var(
        "CUDA_VISIBLE_DEVICES", ",".join(map(str, indices)) if indices else "-1"
    )  # TODO(raz): support the case when this env var already exists

    # TODO(raz): should we set "CUDA_DEVICE_ORDER" as well?


def attach(
    *,
    index: Optional[int] = None,
    gpus: Optional[int] = None,
    allow_over_subscription: bool = False,
) -> Iterable[int]:
    """Attaches devices to the current environment.

    Attaching to a specific device if an index is specified.
    Attaching to a some devices if count is specified.
    Otherwise, the device count is taken from the environment configuration.

    Does not detach devices if already attached to more devices.
    """

    if index is not None and gpus is not None:
        raise ValueError(
            'Can\'t use both "index" and "count" in genv.sdk.devices.attach()'
        )

    if not env.active():
        raise RuntimeError("Not running in an active environment")

    config = env.configuration()

    kwargs = {}
    if index is not None:
        kwargs["index"] = index
    elif gpus is not None:
        kwargs["gpus"] = gpus
    else:
        kwargs["gpus"] = config.gpus

    with genv.utils.global_lock():
        indices = genv.core.devices.attach(
            env.eid(),
            **kwargs,
            gpu_memory=config.gpu_memory,
            allow_over_subscription=allow_over_subscription,
        )

    _update_env(indices)

    return indices


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


def detach(index: Optional[int] = None) -> Iterable[int]:
    """Detaches the current environment from devices.

    Detaches from a specific device if an index is specified.
    Otherwise, detaches from all devices.

    Raises RuntimeError if not running in an active environment.
    """

    if not env.active():
        raise RuntimeError("Not running in an active environment")

    with genv.utils.global_lock():
        indices = genv.core.devices.detach(env.eid(), index)

    _update_env(indices)

    return indices


def refresh_attached() -> Iterable[int]:
    """Refreshes attached devices.

    Raises RuntimeError if not running in an active environment.
    """

    if not env.active():
        raise RuntimeError("Not running in an active environment")

    with genv.utils.global_lock():
        indices = genv.core.devices.attached(env.eid())

    _update_env(indices)

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
