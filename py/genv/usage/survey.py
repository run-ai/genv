from typing import Iterable, Union
from .envs import Env
from .processes import Process
from .snapshot import Snapshot
from .report import Report


class Survey:
    def __init__(self) -> None:
        self._processes_to_terminate = set()
        self._envs_to_detach = set()

    def terminate(self, process: Process) -> None:
        self._processes_to_terminate.add(process)

    def detach(self, envs: Union[Env, Iterable[Env]], index: int) -> None:
        if isinstance(envs, Env):
            envs = [envs]

        self._envs_to_detach.update((env, index) for env in envs)

    def report(self, snapshot: Snapshot) -> Report:
        return Report(
            list(
                self._processes_to_terminate.union(
                    set(
                        process
                        for env, index in self._envs_to_detach
                        for process in snapshot.processes
                        if process.eid == env.eid
                        and index in [usage.index for usage in process.used_gpu_memory]
                    )
                )
            ),
            list(self._envs_to_detach),
        )
