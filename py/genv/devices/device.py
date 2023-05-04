from dataclasses import dataclass
from typing import Iterable, Optional

from genv.utils import memory_to_bytes


@dataclass
class Device:
    @dataclass
    class Attachement:
        eid: str
        gpu_memory: Optional[str]
        time: str

    index: int
    total_memory: str
    attachments: Iterable[Attachement]

    @property
    def eids(self) -> Iterable[str]:
        return [attachment.eid for attachment in self.attachments]

    @property
    def attached(self) -> bool:
        return len(self.eids) > 0

    @property
    def detached(self) -> bool:
        return len(self.eids) == 0

    @property
    def total_memory_bytes(self) -> int:
        """
        Returns the device total memory in bytes.
        """
        return memory_to_bytes(self.total_memory)

    @property
    def available_memory_bytes(self) -> int:
        """
        Returns the device available memory in bytes.
        """
        available_bytes = memory_to_bytes(self.total_memory)

        for attachment in self.attachments:
            available_bytes -= memory_to_bytes(
                attachment.gpu_memory or self.total_memory
            )

        return max(available_bytes, 0)

    def available(self, gpu_memory: Optional[str]) -> bool:
        """
        Returns is the device is available with respect to the given memory specification.
        If memory is specified, checks if this amount is available.
        Otherwise, checks if the device is detached.
        """
        if gpu_memory is None:
            return self.detached

        return self.available_memory_bytes >= memory_to_bytes(gpu_memory)

    def filter(self, *, eids: Iterable[str]):
        """
        Returns a new device with only the given environment identifiers.
        """
        return Device(
            self.index,
            self.total_memory,
            [attachment for attachment in self.attachments if attachment.eid in eids],
        )

    def attach(self, eid: str, gpu_memory: Optional[str], time: str) -> None:
        """
        Attaches an environment.
        """
        self.attachments.append(Device.Attachement(eid, gpu_memory, time))

    def detach(self, eid: str) -> None:
        """
        Detaches an environment.
        """
        for index, attachment in enumerate(self.attachments):
            if attachment.eid == eid:
                del self.attachments[index]
