from contextlib import contextmanager
from datetime import datetime
import json
import os
from typing import Any, Callable, Dict, Optional, Type, Union

from .os_ import access_lock

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


@contextmanager
def access_json(
    filename: str,
    factory: Callable[[], Dict],
    *,
    convert: Optional[Callable[[Any], Any]] = None,
    reset: bool = False,
    json_decoder: Optional[Type[json.JSONDecoder]] = None,
    json_encoder: Optional[Type[json.JSONEncoder]] = None,
):
    """
    This function returns a json object representing a genv state data.
    The state object will either be created or loaded from a cache file, and updated with the correct data.
    At the end of the caller process, the state object will be writen into the cache file.


    :param filename: A filename of a cache file holding the relevant state object.
            The base path of the file is either GENV_TMPDIR (if defined) or /var/tmp/genv.
    :param factory: A function creating a "clean" instance of the state object
    :param convert: A convertor function mutating the state object
                     to the correct form (backward compatibility / updating)
    :param reset: If the reset flag is on,
    :return:
    """
    path = get_temp_file_path(filename)

    with access_lock(f"{path}.lock"):
        if os.path.exists(path) and not reset:
            with open(path) as f:
                o = json.load(f, cls=json_decoder)

                if convert:
                    o = convert(o)
        else:
            o = factory()

        yield o

        # TODO(raz): are probably relying on the umask being set to 0 thanks to access_lock().
        # this is not part of the API of the method so we probably need to do it here as well.
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
