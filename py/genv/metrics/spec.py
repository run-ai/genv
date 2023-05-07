from dataclasses import dataclass
from typing import Callable, Iterable, Optional, Tuple

from genv.entities import Snapshot

from .type import Type

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
    filter: Optional[Callable[[Iterable[str], Snapshot], bool]] = None
