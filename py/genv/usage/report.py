from dataclasses import dataclass
from typing import Optional, Set, Tuple

from .process import Process


@dataclass
class Report:
    processes_to_terminate: Set[Process]
    envs_to_detach: Set[Tuple[str, int, Optional[str]]]
