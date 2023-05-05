from dataclasses import dataclass
from typing import Dict

from genv.entities import Envs
from genv.processes.snapshot import Snapshot as Processes


@dataclass
class Report:
    terminate: Processes
    detach: Dict[int, Envs]

    def __bool__(self) -> bool:
        return len(self.terminate) > 0 or len(self.detach) > 0
