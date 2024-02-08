from dataclasses import dataclass
from typing import Any, Callable, Iterable, Optional, Tuple

from genv.entities import Snapshot

from .type import Type


@dataclass
class Spec:
    """
    A metric specification.

    :param type: Metric group type.
    :param name: Metric name.
    :param documentation: A short description of the metric.
    :param labelnames: Metric label names.
    :param convert: A lambda converting the input data to a metric value; input data type varies per metric.
    :param filter: A lambda for cleaning up expired label names according to the given input data; input data type varies per metric.
    """

    type: Type
    name: str
    documentation: str
    labelnames: Tuple[str] = ()
    convert: Optional[Callable[[Any], float]] = None
    filter: Optional[Callable[[Iterable[str], Snapshot], bool]] = None
