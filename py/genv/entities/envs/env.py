from dataclasses import dataclass
from typing import Callable, Iterable, Optional

import genv.utils


@dataclass
class Env:
    @dataclass
    class Config:
        name: Optional[str]
        gpu_memory: Optional[str]
        gpus: Optional[int]

    eid: str
    uid: int
    creation: str
    username: Optional[str]
    config: Config
    pids: Iterable[int]
    kernel_ids: Iterable[str]

    @property
    def time_since(self) -> str:
        return genv.utils.time_since(self.creation)

    @property
    def active(self) -> bool:
        return len(self.pids) > 0 or len(self.kernel_ids) > 0

    def __hash__(self) -> int:
        return self.eid.__hash__()

    def cleanup(
        self,
        *,
        poll_pid: Callable[[int], bool] = genv.utils.poll_pid,
        poll_kernel: Callable[[str], bool] = genv.utils.poll_jupyter_kernel,
    ):
        """
        Cleans up in place.
        """
        self.pids = [pid for pid in self.pids if poll_pid(pid)]

        self.kernel_ids = [
            kernel_id for kernel_id in self.kernel_ids if poll_kernel(kernel_id)
        ]

    def attach(
        self, *, pid: Optional[int] = None, kernel_id: Optional[str] = None
    ) -> None:
        """
        Attaches a process or a Jupyter kernel to an environment.
        """
        if pid is not None:
            self.pids.append(pid)

        if kernel_id is not None:
            self.kernel_ids.append(kernel_id)
