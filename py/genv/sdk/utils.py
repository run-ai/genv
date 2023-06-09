from contextlib import contextmanager
import os
from typing import Any, Iterable, Optional, Union


def get_temp_env_vars(
    *, ignore: Optional[Union[str, Iterable[str]]] = None
) -> Iterable[str]:
    """Returns the temporary variables"""

    if ignore is None:
        ignore = []
    elif isinstance(ignore, str):
        ignore = [ignore]

    return [
        name
        for name in os.environ.get("GENV_ENVS", "").split(":")
        if (len(name) and (name not in ignore))
    ]


def set_temp_env_var(name: str, value: Any) -> None:
    """Sets a temporary environment variable"""

    os.environ[name] = str(value)
    os.environ["GENV_ENVS"] = ":".join(get_temp_env_vars(ignore=name) + [name])


def unset_temp_env_var(name: str) -> None:
    """Unsets a temporary environment variable if set"""

    os.environ.pop(name, None)
    os.environ["GENV_ENVS"] = ":".join(get_temp_env_vars(ignore=name))


def unset_temp_env_vars() -> None:
    """Unsets all temporary environment variables"""

    for name in get_temp_env_vars():
        unset_temp_env_var(name)

    os.environ.pop("GENV_ENVS", None)


@contextmanager
def temp_env_vars() -> None:
    """Context manager for unsetting temporary environment variables"""

    try:
        yield
    finally:
        unset_temp_env_vars()
