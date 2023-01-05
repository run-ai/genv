from dataclasses import dataclass
from typing import Iterable, Tuple

from .envs import Env
from .processes import Process


@dataclass
class Report:
    processes_to_terminate: Iterable[Process]
    envs_to_detach: Iterable[Tuple[Env, int]]
