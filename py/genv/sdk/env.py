from contextlib import contextmanager
import os
from typing import Optional

import genv.utils
from genv.entities import Env
import genv.core

from . import devices
from .utils import set_temp_env, temp_env


def eid() -> Optional[str]:
    """Returns the current environment identifier or None if not running in one"""

    return os.environ.get("GENV_ENVIRONMENT_ID")


def active() -> bool:
    """Returns whether running in an active environment"""

    return eid() is not None


def load_configuration() -> Env.Config:
    """Loads the environment configuration.

    Raises RuntimeError if not running in an active environment.
    """

    if not active():
        raise RuntimeError("Not running in an active environment")

    with genv.utils.global_lock():
        config = genv.core.envs.configuration(eid())

    for name, value in [
        ("GENV_ENVIRONMENT_NAME", config.name),
        ("GENV_GPU_MEMORY", config.gpu_memory),
        ("GENV_GPUS", config.gpus),
    ]:
        if value:
            set_temp_env(name, value)

    return config


@contextmanager
def activate(*, eid: Optional[str] = None) -> None:
    """A context manager for activating an environment for the current process.

    Raises RuntimeError if already running in an active environment.

    :param eid: Environment identifier
    """

    if active():
        raise RuntimeError("Already running in an active environment")

    pid = os.getpid()
    eid = eid or str(pid)

    with temp_env():
        set_temp_env("GENV_PYTHON", "1")
        set_temp_env("GENV_ENVIRONMENT_ID", eid)

        with genv.utils.global_lock():
            genv.core.envs.activate(
                eid, uid=os.getuid(), username=os.getlogin(), pid=pid
            )

        load_configuration()

        devices.load_attached()

        # TODO(raz): support configuring environment and attaching devices

        try:
            yield
        finally:
            with genv.utils.global_lock():
                genv.core.envs.deactivate(pid=pid)
