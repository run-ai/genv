from typing import Iterable

from genv.entities import Snapshot

from .metric import Metric
from .spec import Spec
from .type import Type


class Collection:
    """
    A metric collection.
    """

    def __init__(self, specs: Iterable[Spec]) -> None:
        self._metrics = [
            Metric(
                spec.name,
                spec.documentation,
                spec.labelnames,
                type=spec.type,
                convert=spec.convert,
                filter=spec.filter,
            )
            for spec in specs
        ]

    def __iter__(self):
        return self._metrics.__iter__()

    def __getitem__(self, name: str) -> Metric:
        return next(metric for metric in self if metric.name == name)

    def _find(self, type: Type) -> Iterable[Metric]:
        """
        Returns all metrics of the given type.
        """
        return [metric for metric in self if metric.type == type]

    def cleanup(self, snapshot: Snapshot) -> None:
        """
        Cleans up metric label values.
        """
        for metric in self:
            if not metric.filter:
                continue

            metric.cleanup(lambda label_set: metric.filter(label_set, snapshot))

    def update(self, snapshot: Snapshot, labels: dict = {}) -> None:
        """
        Updates metrics according to the given snapshot.
        """
        for group in [
            self._system,
            self._env,
            self._process,
            self._user,
        ]:
            group(snapshot, labels)

    def _system(self, snapshot: Snapshot, labels: dict) -> None:
        """
        Updates system-wide metrics.
        """
        for metric in self._find(Type.System):
            metric.labels(**labels).update(snapshot)

    def _env(self, snapshot: Snapshot, labels: dict) -> None:
        """
        Updates per-environment metrics.
        """
        for env in snapshot.envs:
            env_snapshot = snapshot.filter(eid=env.eid)

            for metric in self._find(Type.Environment):
                metric.labels(eid=env.eid, **labels).update(env_snapshot)

    def _process(self, snapshot: Snapshot, labels: dict) -> None:
        """
        Updates per-process metrics.
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

            for metric in self._find(Type.User):
                metric.labels(username=username, **labels).update(user_snapshot)
