from typing import Callable, Iterable, Optional, Tuple

import prometheus_client

from genv.snapshot import Snapshot
from genv.metrics.spec import Type


class Metric(prometheus_client.Gauge):
    """
    A Genv metric.
    """

    def __init__(
        self,
        name: str,
        documentation: str,
        labelnames: Tuple[str],
        *,
        type: Type,
        convert: Optional[Callable[[Snapshot], float]],
        filter: Optional[Callable[[Tuple[str], Snapshot], bool]],
        **kwargs,
    ):
        super().__init__(name, documentation, labelnames, **kwargs)
        self._kwargs["type"] = self.type = type
        self._kwargs["convert"] = self.convert = convert
        self._kwargs["filter"] = self.filter = filter

    @property
    def name(self) -> str:
        return self._name

    def update(self, snapshot: Snapshot) -> None:
        """
        Update the metric value according to the given snapshot.
        Note that some metrics expect the snapshot to be already filtered.
        """
        if self.convert is None:
            raise RuntimeError(
                "Conversion function must be provided when using snapshots"
            )

        self.set(self.convert(snapshot))

    def labels(self, *labelvalues, **labelkwargs):
        """
        Sets metric label values if passed.
        """
        if labelvalues or labelkwargs:
            return super().labels(*labelvalues, **labelkwargs)

        return self

    def cleanup(self, snapshot: Snapshot) -> None:
        """
        Cleans up outdated metric label values.
        """
        if self.filter is None:
            return

        for label_set in self._label_sets():
            if not self.filter(label_set, snapshot):
                self.remove(*label_set)

    def _label_sets(self) -> Iterable[str]:
        """
        Returns the current label value sets.
        """
        with self._lock:
            return list(self._metrics.keys())
