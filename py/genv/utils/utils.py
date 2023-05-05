from contextlib import contextmanager
from datetime import datetime
import json
import os
from typing import Any, Callable, Optional, Type, TypeVar, Union

from .os_ import Umask, access_lock

T = TypeVar("T")

DATETIME_FMT = "%d/%m/%Y %H:%M:%S"
MEMORY_TO_BYTES_MULTIPLIERS_DICT = {
    "b": 1,
    "k": 1000,
    "m": 1000 * 1000,
    "g": 1000 * 1000 * 1000,
    "ki": 1024,
    "mi": 1024 * 1024,
    "gi": 1024 * 1024 * 1024,
}


def get_temp_file_path(filename: str) -> str:
    """
    Returns the path of a file with the provided name in the Genv temporary directory.
    """
    return os.path.join(os.environ.get("GENV_TMPDIR", "/var/tmp/genv"), filename)


def load_state(
    path: str,
    *,
    creator: Callable[[], T],
    cleaner: Callable[[T], None],
    converter: Optional[Callable[[Any], T]] = None,
    json_decoder: Optional[Type[json.JSONDecoder]] = None,
    cleanup: bool = True,
    reset: bool = False,
) -> T:
    """
    Loads a state file.
    """
    if os.path.exists(path) and not reset:
        with open(path) as f:
            o = json.load(f, cls=json_decoder)

        if converter:
            o = converter(o)

        if cleanup:
            cleaner(o)
    else:
        o = creator()

    return o


def save_state(
    o: Any,
    path: str,
    *,
    json_encoder: Optional[Type[json.JSONEncoder]] = None,
):
    """
    Saves a state file.
    """
    with Umask(0):
        with open(
            path, "w", opener=lambda path, flags: os.open(path, flags, 0o666)
        ) as f:
            json.dump(o, f, cls=json_encoder, indent=2)


def memory_to_bytes(cap: str) -> int:
    """
    Convert memory string to an integer value in bytes.
    """
    for unit, multiplier in MEMORY_TO_BYTES_MULTIPLIERS_DICT.items():
        if cap.endswith(unit):
            return int(cap.replace(unit, "")) * multiplier

    return int(cap)  # the value is already in bytes if no unit was specified


# TODO(raz): support detecting the most suitable units automatically
def bytes_to_memory(bytes: int, unit: str, suffix: bool = True) -> str:
    """
    Convert bytes to a memory string.
    """
    s = f"{bytes // MEMORY_TO_BYTES_MULTIPLIERS_DICT[unit]}"

    if suffix:
        s = f"{s}{unit}"

    return s


def memory_to_memory(memory: str, unit: str, suffix: bool = True) -> str:
    """
    Convert memory string to a memory string in another unit.
    """
    return bytes_to_memory(bytes=memory_to_bytes(memory), unit=unit, suffix=suffix)


def time_since(dt: Union[str, datetime]) -> str:
    """
    This function returns a human readable string describing the amount of time passed since 'dt'
    :param dt: The base time to calculate from. Can be either string or datetime
    :return: a human readable string describing the amount of time passed since 'dt'
    """
    if isinstance(dt, str):
        dt = datetime.strptime(dt, DATETIME_FMT)

    value = int((datetime.now() - dt).total_seconds())
    unit = "second"

    for amount, next_units in [
        (60, "minute"),
        (60, "hour"),
        (24, "day"),
        (7, "week"),
    ]:
        if value < amount:
            break

        value, _ = divmod(value, amount)
        unit = next_units

    if value > 1:
        unit = f"{unit}s"

    return f"{value} {unit} ago"


@contextmanager
def global_lock() -> None:
    """
    Locks the global lock.
    """
    with access_lock(get_temp_file_path("genv.lock")):
        yield
