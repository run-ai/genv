from dataclasses import dataclass
import sys
from typing import Iterable, Optional

import genv.utils


@dataclass
class Process:
    """
    A compute running process.
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
            return genv.utils.memory_to_bytes(self.gpu_memory)

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
            return genv.utils.get_process_environ(pid).get("GENV_ENVIRONMENT_ID")
        except PermissionError:
            print(
                f"[WARNING] Not enough permissions to query environment of process {pid}",
                file=sys.stderr,
            )
        except FileNotFoundError:
            print(f"[DEBUG] Process {pid} already terminated", file=sys.stderr)


@dataclass
class Processes:
    """
    A collection of processes.
    """

    processes: Iterable[Process]

    @property
    def pids(self) -> Iterable[int]:
        return [process.pid for process in self.processes]

    def __iter__(self):
        return self.processes.__iter__()

    def __len__(self):
        return self.processes.__len__()

    def __getitem__(self, pid: int) -> Process:
        return next(process for process in self.processes if process.pid == pid)

    def filter(
        self,
        deep: bool = True,
        *,
        pids: Optional[Iterable[int]] = None,
        eid: Optional[str] = None,
        eids: Optional[Iterable[str]] = None,
        index: Optional[int] = None,
    ):
        """
        Returns a new filtered collection.

        :param deep: Perform deep filtering
        :param pids: Process identifiers to keep
        :param eid: Environment identifier to keep
        :param eids: Environment identifiers to keep
        :param username: Username to keep
        """
        if eids:
            eids = set(eids)

        if eid:
            if not eids:
                eids = set()

            eids.add(eid)

        processes = self.processes

        if pids is not None:
            processes = [process for process in processes if process.pid in pids]

        if eids is not None:
            processes = [process for process in processes if process.eid in eids]

        if index is not None:
            if deep:
                processes = [process.filter(index=index) for process in processes]

            processes = [process for process in processes if index in process.indices]

        return Processes(processes)
