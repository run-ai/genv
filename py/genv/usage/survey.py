from typing import Optional

from .process import Process
from .snapshot import Snapshot
from .report import Report


class Survey:
    def __init__(self) -> None:
        self._processes_to_terminate = set()
        self._envs_to_detach = set()

    def terminate(self, process: Process) -> None:
        self._processes_to_terminate.add(process)

    def detach(self, eid: str, index: int, username: Optional[str]) -> None:
        self._envs_to_detach.add((eid, index, username))

    def report(self, snapshot: Snapshot) -> Report:
        return Report(
            self._processes_to_terminate.union(
                set(
                    process
                    for eid, index, _ in self._envs_to_detach
                    for process in snapshot.processes
                    if process.eid == eid and process.gpu_index == index
                )
            ),
            self._envs_to_detach,
        )
