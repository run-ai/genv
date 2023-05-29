from contextlib import contextmanager
import os
from typing import Any


def set_temp_env(name: str, value: Any) -> None:
    """Sets a temporary environment variable"""

    os.environ[name] = str(value)
    os.environ["GENV_ENVS"] = os.environ.get("GENV_ENVS", "") + f":{name}"


def unset_temp_env(name: str) -> None:
    """Unsets a temporary environment variable if set"""

    os.environ.pop(name, None)


def unset_temp_envs() -> None:
    """Unsets all temporary environment variables"""

    for name in [
        name for name in os.environ.get("GENV_ENVS", "").split(":") if name
    ] + ["GENV_ENVS"]:
        unset_temp_env(name)


@contextmanager
def temp_env() -> None:
    """Context manager for unsetting temporary environment variables"""

    try:
        yield
    finally:
        unset_temp_envs()
