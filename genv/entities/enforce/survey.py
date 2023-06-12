from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, Optional, Set

from ..core import Snapshot

from . import Report


@dataclass
class Survey:
    snapshot: Snapshot
    hostname: Optional[str] = None

    _pids: Set[int] = field(default_factory=set, init=False)
    _eids: Dict[int, Set[str]] = field(
        default_factory=lambda: defaultdict(set), init=False
    )

    def terminate(self, *pids: int) -> None:
        self._pids.update(pids)

    def detach(self, index: int, *eids: str) -> None:
        self._eids[index].update(eids)

        self.terminate(
            *(
                process.pid
                for eid in eids
                for process in self.snapshot.processes.filter(eid=eid, index=index)
            )
        )

    @property
    def report(self) -> Report:
        return Report(
            terminate=self.snapshot.processes.filter(deep=False, pids=self._pids),
            detach={
                index: self.snapshot.envs.filter(deep=False, eids=eids)
                for index, eids in self._eids.items()
            },
        )
