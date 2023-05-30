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


def _set_configuration(config: Env.Config) -> None:
    """Sets the configuration environment variables"""

    for name, value in [
        ("GENV_ENVIRONMENT_NAME", config.name),
        ("GENV_GPU_MEMORY", config.gpu_memory),
        ("GENV_GPUS", config.gpus),
    ]:
        if value:
            set_temp_env(name, value)


def configure(config: Env.Config) -> None:
    """Configures the current environment"""

    if not active():
        raise RuntimeError("Not running in an active environment")

    with genv.utils.global_lock():
        genv.core.envs.configure(eid(), config)

    _set_configuration(config)


def configuration() -> Env.Config:
    """Returns the current environment configuration.

    Raises RuntimeError if not running in an active environment.
    """

    if not active():
        raise RuntimeError("Not running in an active environment")

    name = os.environ.get("GENV_ENVIRONMENT_NAME")
    gpu_memory = os.environ.get("GENV_GPU_MEMORY")
    gpus = os.environ.get("GENV_GPUS")

    return Env.Config(
        name=name, gpu_memory=gpu_memory, gpus=int(gpus) if gpus else None
    )


def load_configuration() -> Env.Config:
    """Loads the environment configuration.

    Raises RuntimeError if not running in an active environment.
    """

    if not active():
        raise RuntimeError("Not running in an active environment")

    with genv.utils.global_lock():
        config = genv.core.envs.configuration(eid())

    _set_configuration(config)

    return config


@contextmanager
def activate(*, eid: Optional[str] = None, config: Optional[Env.Config] = None) -> None:
    """A context manager for activating an environment for the current process.

    Configures the environment if configuration is specified.
    Attaches devices if device count is configured.

    Raises RuntimeError if already running in an active environment.

    :param eid: Environment identifier
    :param config: Environment configuration
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

        if config is not None:
            configure(config)
        else:
            load_configuration()

        indices = devices.load_attached()

        if not indices:
            devices.attach()

        try:
            yield
        finally:
            with genv.utils.global_lock():
                genv.core.envs.deactivate(pid=pid)
