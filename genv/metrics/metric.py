from typing import Iterable

import prometheus_client

from .spec import Spec


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
        spec: Spec,
        **kwargs,
    ):
        super().__init__(name, documentation, labelnames, **kwargs)
        self._kwargs["spec"] = self.spec = spec

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
