from contextlib import contextmanager
import getpass
import os
from pathlib import Path
from typing import Optional

import genv.utils
from genv.entities import Env
import genv.core

from . import devices
from .utils import set_temp_env_var, temp_env_vars, unset_temp_env_var


def eid() -> Optional[str]:
    """Returns the current environment identifier or None if not running in one"""

    return os.environ.get("GENV_ENVIRONMENT_ID")


def active() -> bool:
    """Returns whether running in an active environment"""

    return eid() is not None


def home() -> Optional[Path]:
    """Returns the configuration directory for this environment if exists"""

    for alt in [Path.cwd(), Path.home()]:
        path = alt.joinpath(".genv")

        if path.is_dir():
            return path


def _update_env(config: Env.Config) -> None:
    """Updates the configuration environment variables"""

    for name, value in [
        ("GENV_ENVIRONMENT_NAME", config.name),
        ("GENV_GPU_MEMORY", config.gpu_memory),
        ("GENV_GPUS", config.gpus),
    ]:
        if value is not None:
            set_temp_env_var(name, value)
        else:
            unset_temp_env_var(name)


def configure(config: Env.Config) -> None:
    """Configures the current environment"""

    if not active():
        raise RuntimeError("Not running in an active environment")

    with genv.utils.global_lock():
        genv.core.envs.configure(eid(), config)

    _update_env(config)


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


def refresh_configuration() -> Env.Config:
    """Refreshes the environment configuration.

    Raises RuntimeError if not running in an active environment.
    """

    if not active():
        raise RuntimeError("Not running in an active environment")

    with genv.utils.global_lock():
        config = genv.core.envs.configuration(eid())

    _update_env(config)

    return config


def load_configuration() -> Env.Config:
    """Loads configuration from disk.

    Raises RuntimeError if not running in an active environment.
    """

    if not active():
        raise RuntimeError("Not running in an active environment")

    config = Env.Config()

    home_dir = home()

    if home_dir:
        config.load(home_dir)

    _update_env(config)

    return config


def save_configuration() -> None:
    """Saves the current configuration to disk.

    Raises RuntimeError if not running in an active environment.
    """

    home_dir = home()

    if home_dir is not None:
        config = configuration()

        config.save(home_dir)


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

    with temp_env_vars():
        set_temp_env_var("GENV_PYTHON", "1")
        set_temp_env_var("GENV_ENVIRONMENT_ID", eid)

        with genv.utils.global_lock():
            genv.core.envs.activate(
                eid, uid=os.getuid(), username=getpass.getuser(), pid=pid
            )

        if config is not None:
            configure(config)
        else:
            config = refresh_configuration()

        indices = devices.refresh_attached()

        if not indices:
            devices.attach()

        try:
            yield
        finally:
            with genv.utils.global_lock():
                genv.core.envs.deactivate(pid=pid)
