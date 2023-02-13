from dataclasses import dataclass
from typing import Dict

from .. import envs
from .. import processes


@dataclass
class Report:
    terminate: processes.Snapshot
    detach: Dict[int, envs.Snapshot]

    def __bool__(self) -> bool:
        return len(self.terminate) > 0 or len(self.detach) > 0
