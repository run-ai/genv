from typing import Callable, Iterable, Optional

import prometheus_client

from genv.entities import Snapshot

from .spec import Type


class Metric(prometheus_client.Gauge):
    """
    A Genv metric.
    """

    def __init__(
        self,
        name: str,
        documentation: str,
        labelnames: Iterable[str],
        *,
        type: Type,
        convert: Optional[Callable[[Snapshot], float]],
        filter: Optional[Callable[[Iterable[str], Snapshot], bool]],
        **kwargs,
    ):
        super().__init__(name, documentation, labelnames, **kwargs)
        self._kwargs["type"] = self.type = type
        self._kwargs["convert"] = self.convert = convert
        self._kwargs["filter"] = self.filter = filter

    @property
    def name(self) -> str:
        return self._name

    def labels(self, *labelvalues, **labelkwargs):
        """
        Sets metric label values if passed.
        """
        if labelvalues or labelkwargs:
            return super().labels(*labelvalues, **labelkwargs)

        return self

    def cleanup(self, filter: Callable[[Iterable[str]], bool]) -> None:
        """
        Cleans up metric label values.
        """
        with self._lock:
            label_sets = list(self._metrics.keys())

        for label_set in label_sets:
            if not filter(label_set):
                self.remove(*label_set)

    def update(self, snapshot: Snapshot) -> None:
        """
        Updates the metric value according to the given snapshot.
        Note that some metrics expect the snapshot to be already filtered.
        """
        if self.convert is None:
            raise RuntimeError(
                "Conversion function must be provided when using snapshots"
            )

        self.set(self.convert(snapshot))
