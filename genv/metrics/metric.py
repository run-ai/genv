from typing import Any, Callable, Iterable, Optional

import prometheus_client

from genv.entities import Snapshot

from .type import Type


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
        convert: Optional[Callable[[Any], float]],
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

    def label_sets(self) -> Iterable[str]:
        """Returns all metric labels."""

        if not self._is_parent():
            return []

        with self._lock:
            return list(self._metrics.keys())
