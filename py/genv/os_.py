from contextlib import contextmanager
import fcntl
import os
import platform
import signal
import subprocess
from typing import Dict, Iterable


@contextmanager
def Umask(value: int = 0):
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


def get_process_environ(pid: int) -> Dict[str, str]:
    """
    Returns the environment variables of the process with the given identifier.

    Raises 'NotImplementedError' if running in a non-Linux platform as it relies on the Linux proc filesystem.
    Raises 'FileNotFoundError' if no such process.
    Raises 'PermissionError' if there is no sufficient permissions.

    """
    # TODO(raz): support this with psutil.Process().eniron() probably
    if platform.system() != "Linux":
        raise NotImplementedError(
            "genv.os_.get_process_environ is not supported in platforms other than Linux"
        )

    with open(f"/proc/{pid}/environ", "r") as f:
        return {
            variable: value
            for variable, value in (
                line.split("=", 1) for line in f.read().split("\x00") if line
            )
        }


def pgrep(name: str) -> Iterable[int]:
    """
    Returns the identifiers of processes with the given name.
    """
    return [
        int(pid)
        for pid in subprocess.check_output(
            f"pgrep {name} || true", shell=True
        ).splitlines()
    ]


def cmdline(pid: int) -> Iterable[str]:
    """
    Returns the cmdline of the process with the given identifier.
    """
    return (
        subprocess.check_output(f"tr '\\0' ' ' </proc/{pid}/cmdline", shell=True)
        .decode("utf-8")
        .split()
    )


def terminate(pid: int) -> None:
    """
    Terminates the running process with the given pid by sending the signal SIGTERM to it.

    Raises 'ProcessLookupError' if no such process.
    Raises 'PermissionError' if there is no sufficient permissions.
    """
    if int(os.environ.get("GENV_TERMINATE_PROCESSES", "1")) == 0:
        return

    os.kill(pid, signal.SIGTERM)
