from contextlib import contextmanager
import fcntl
import os


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
