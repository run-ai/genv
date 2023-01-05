from dataclasses import dataclass
from typing import Iterable

import genv.devices


@dataclass
class Device:
    index: int
    eids: Iterable[str]


def snapshot() -> Iterable[Device]:
    return [Device(index, d["eids"]) for index, d in genv.devices.ps().items()]
