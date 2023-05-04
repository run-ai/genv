from dataclasses import dataclass
from typing import Iterable, Optional

from genv.processes.process import Process


@dataclass
class Snapshot:
    """
    A snapshot of running processes.
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
        Returns a new filtered snapshot.

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

        return Snapshot(processes)
