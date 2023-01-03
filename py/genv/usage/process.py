from dataclasses import dataclass
from typing import Optional

import genv.nvidia_smi


@dataclass
class Process(genv.nvidia_smi.Process):
    eid: Optional[str]

    def __hash__(self) -> int:
        return super().__hash__()
