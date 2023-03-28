from dataclasses import dataclass
from typing import Callable, Optional, Tuple
from genv.metrics.type import Type

from genv.snapshot import Snapshot


@dataclass
class Spec:
    """
    A metric specification.
    """

    type: Type
    name: str
    documentation: str
    labelnames: Tuple[str] = ()
    convert: Optional[Callable[[Snapshot], float]] = None
    filter: Optional[Callable[[Tuple[str], Snapshot], bool]] = None
