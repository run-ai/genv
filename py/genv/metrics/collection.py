from dataclasses import dataclass
from typing import Generic, Iterable, TypeVar

from genv.metrics.metric import Metric
from genv.metrics.type import Type
from genv.snapshot import Snapshot


T = TypeVar("T", bound=Metric)


@dataclass
class Collection(Generic[T]):
    """
    A metric collection.
    """

    metrics: Iterable[T]

    def filter(self, type: Type):
        """
        Returns a new filtered collection.
        """
        return Collection([metric for metric in self.metrics if metric.type == type])

    def __iter__(self):
        return self.metrics.__iter__()

    def __getitem__(self, name: str) -> T:
        return next(metric for metric in self.metrics if metric.name == name)

    def update(self, snapshot: Snapshot, labels: dict = {}):
        """
        Updates metics according to the given snapshot.
        """
        for group in [
            self._system,
            self._env,
            self._device,
            self._user,
        ]:
            group(snapshot, labels)

    def _system(self, snapshot: Snapshot, labels: dict) -> None:
        """
        Updates system-wide metrics.
        """
        for metric in self.filter(Type.System):
            metric.labels(**labels).update(snapshot)

    def _env(self, snapshot: Snapshot, labels: dict) -> None:
        """
        Updates per-environment metrics.
        """
        for env in snapshot.envs:
            env_snapshot = snapshot.filter(eid=env.eid)

            for metric in self.filter(Type.Environment):
                metric.labels(eid=env.eid, **labels).update(env_snapshot)

    def _device(self, snapshot: Snapshot, labels: dict) -> None:
        """
        Updates per-device metrics.
        """
        for process in snapshot.processes:
            pid = process.pid
            eid = process.eid or ""

            self["genv_process_devices_total"].labels(pid=pid, eid=eid, **labels).set(
                len(process.indices)
            )

            for usage in process.used_gpu_memory:
                self["genv_process_used_gpu_memory_bytes"].labels(
                    pid=pid, eid=eid, device=usage.index, **labels
                ).set(usage.bytes)

    def _user(self, snapshot: Snapshot, labels: dict) -> None:
        """
        Updates per-user metrics.
        """
        for username in snapshot.envs.usernames:
            user_snapshot = snapshot.filter(username=username)

            for metric in self.filter(Type.User):
                metric.labels(username=username, **labels).update(user_snapshot)
