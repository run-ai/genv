from dataclasses import dataclass
import sys
from typing import Iterable, Optional
from genv import os_

from genv.utils import memory_to_bytes


@dataclass
class Process:
    """
    A compute running process either from an environment or not.
    """

    @dataclass
    class Usage:
        """
        The GPU index and amount of GPU memory used by the process.
        """

        index: int
        gpu_memory: str

        @property
        def bytes(self) -> int:
            return memory_to_bytes(self.gpu_memory)

    pid: int
    used_gpu_memory: Iterable[Usage]
    eid: Optional[str]

    @property
    def indices(self) -> Iterable[int]:
        return [usage.index for usage in self.used_gpu_memory]

    @property
    def total_bytes(self) -> int:
        return sum(usage.bytes for usage in self.used_gpu_memory)

    def __hash__(self) -> int:
        return self.pid.__hash__()

    def filter(self, *, index: int):
        """
        Returns a new process with information only of the given device index.
        """
        return Process(
            self.pid,
            [usage for usage in self.used_gpu_memory if usage.index == index],
            self.eid,
        )

    @staticmethod
    def eid(pid: int) -> Optional[str]:
        """
        Returns the environment identifier of the process with the given pid.
        Returns None if the process is not running in an environment or if it could not be queried.
        """
        try:
            return os_.get_process_environ(pid).get("GENV_ENVIRONMENT_ID")
        except PermissionError:
            print(
                f"[WARNING] Not enough permissions to query environment of process {pid}",
                file=sys.stderr,
            )
        except FileNotFoundError:
            print(f"[DEBUG] Process {pid} already terminated", file=sys.stderr)
