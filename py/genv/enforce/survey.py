from typing import Iterable, Set, Tuple, Union

from ..snapshot import Snapshot

from .report import Report


class Survey:
    def __init__(self) -> None:
        self._pids: Set[int] = set()
        self._eids_indices: Set[Tuple[str, int]] = set()

    def terminate(self, pids: Union[int, Iterable[int]]) -> None:
        if isinstance(pids, int):
            pids = [pids]

        self._pids.update(pids)

    def detach(self, eids: Union[str, Iterable[str]], index: int) -> None:
        if isinstance(eids, str):
            eids = [eids]

        self._eids_indices.update((eid, index) for eid in eids)

    def report(self, snapshot: Snapshot) -> Report:
        processes_to_terminate = list(
            snapshot.processes.filter(
                deep=False,
                pids=self._pids.union(
                    set(
                        process.pid
                        for eid, index in self._eids_indices
                        for process in snapshot.processes.filter(eid=eid, index=index)
                    )
                ),
            )
        )

        envs_to_detach = [
            (snapshot.envs[eid], index) for eid, index in self._eids_indices
        ]

        return Report(processes_to_terminate, envs_to_detach)
