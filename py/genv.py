from contextlib import contextmanager
from datetime import datetime
import errno
import fcntl
import json
import os
from pathlib import Path
import subprocess
from typing import Callable, Dict, Optional, Union

DATETIME_FMT = '%d/%m/%Y %H:%M:%S'

def poll_pid(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except OSError as e:
        if e.errno == errno.ESRCH:
            return False
        elif e.errno == errno.EPERM:
            return True
        else:
            raise
    else:
        return True

def poll_kernel(kernel_id: str) -> bool:
    # TODO(raz): what about the case when 'jupyter' is not available in the
    #            environment that we are currently running in?
    #
    # should we ignore such cases and _not_ cleanup kernels if we don't have the 'jupyter' command?
    # should we look for kernel processes similarly to 'ps -ef | grep kernel-'?
    # should we document the kernel json path when activating a kernel, so that the path will
    # be known in other environments as well? what if we don't have read permissions?

    result = subprocess.run(
        ['sh', '-c', f'ls $(jupyter --runtime-dir)/kernel-{kernel_id}.json'],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    return result.returncode == 0

def time_since(dt: Union[str, datetime]) -> str:
    if isinstance(dt, str):
        dt = datetime.strptime(dt, DATETIME_FMT)

    value = int((datetime.now() - dt).total_seconds())
    unit = 'second'

    for amount, next in [
        (60, 'minute'),
        (60, 'hour'),
        (24, 'day'),
        (7, 'week'),
    ]:
        if value < amount:
            break

        value, _ = divmod(value, amount)
        unit = next

    if value > 1:
        unit = f'{unit}s'

    return f'{value} {unit} ago'

@contextmanager
def Umask(value: int=0):
    prev = os.umask(value)
    try:
        yield
    finally:
        os.umask(prev)

class Flock:
    def __init__(self, path: str, mode: int):
        self._path = path
        self._mode = mode

    def __enter__(self):
        self._fd = os.open(self._path, os.O_RDWR | os.O_CREAT | os.O_TRUNC, self._mode)

        try:
            fcntl.flock(self._fd, fcntl.LOCK_EX)
        except (IOError, OSError):
            os.close(self._fd)
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            fcntl.flock(self._fd, fcntl.LOCK_UN)
        finally:
            os.close(self._fd)

@contextmanager
def access_json(filename: str, factory: Callable[[], Dict], *, convert: Optional[Callable[[Dict], None]]=None, reset: bool=False):
    path = os.path.join(os.environ.get('GENV_TMPDIR', '/var/tmp/genv'), filename)

    with Umask(0):
        Path(path).parent.mkdir(parents=True, exist_ok=True, mode=0o777)

        with Flock(f'{path}.lock', 0o666):
            if os.path.exists(path) and not reset:
                with open(path) as f:
                    o = json.load(f)

                    if convert:
                        convert(o)
            else:
                o = factory()

            yield o

            with open(path, 'w', opener=lambda path, flags: os.open(path, flags, 0o666)) as f:
                json.dump(o, f, indent=4)

def memory_to_bytes(cap: str) -> int:
    """
    Convert memory string to an integer value in bytes.
    """
    for unit, multiplier in [
        ('b', 1),
        ('k', 1000),
        ('m', 1000 * 1000),
        ('g', 1000 * 1000 * 1000),
        ('ki', 1024),
        ('mi', 1024 * 1024),
        ('gi', 1024 * 1024 * 1024),
    ]:
        if cap.endswith(unit):
            return int(cap.replace(unit, '')) * multiplier

    return int(cap)  # the value is already in bytes if no unit was specified

def bytes_to_memory(bytes: int, unit: str) -> str:
    """
    Convert bytes to a memory string.
    """
    multipliers = {
        'b': 1,
        'k': 1000,
        'm': 1000 * 1000,
        'g': 1000 * 1000 * 1000,
        'ki': 1024,
        'mi': 1024 * 1024,
        'gi': 1024 * 1024 * 1024,
    }

    return f'{bytes // multipliers[unit]}{unit}'
