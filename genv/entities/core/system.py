from dataclasses import dataclass
from typing import Iterable


@dataclass
class System:
    """System status."""

    @dataclass
    class Genv:
        """Genv status."""

        installed: bool

    @dataclass
    class Device:
        """Device status."""

        index: int
        utilization: int
        temperature: int
        used_memory: str
        total_memory: str

    genv: Genv
    devices: Iterable[Device]
