from dataclasses import dataclass
from typing import Dict, Generic, TypeVar

from genv.metrics.metric import Metric
from genv.metrics.type import Type


T = TypeVar("T", bound=Metric)


@dataclass
class Collection(Generic[T]):
    """
    A metric collection.
    """

    _metrics: Dict[str, T]

    def filter(self, type: Type):
        """
        Returns a new filtered collection.
        """
        return Collection(
            {
                name: metric
                for name, metric in self._metrics.items()
                if metric.type == type
            }
        )

    def __iter__(self):
        return self._metrics.values().__iter__()

    def __getitem__(self, name: str) -> T:
        return self._metrics.__getitem__(name)
