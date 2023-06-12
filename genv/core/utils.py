from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar, Union

import genv.utils

T = TypeVar("T")


class File(Generic[T], ABC):
    """
    A state file on disk.
    """

    def __init__(self, path: str, cleanup: bool = True, reset: bool = False) -> None:
        self._path = path
        self._cleanup = cleanup
        self._reset = reset

    @abstractmethod
    def _create(self) -> T:
        """Creates a new state."""
        pass

    @abstractmethod
    def _clean(self, state: T) -> None:
        """Cleans up state."""
        pass

    def _convert(self, o: Union[Any, T]) -> T:
        """Converts the loaded object if needed."""
        return o

    def load(self) -> T:
        """Loads state from disk."""
        self._state = genv.utils.load_state(
            self._path,
            creator=self._create,
            cleaner=self._clean,
            converter=self._convert,
            json_decoder=genv.serialization.JSONDecoder,
            cleanup=self._cleanup,
            reset=self._reset,
        )

        return self._state

    def save(self) -> None:
        """Saves state to disk."""
        genv.utils.save_state(
            self._state,
            self._path,
            json_encoder=genv.serialization.JSONEncoder,
        )

    def __enter__(self) -> T:
        return self.load()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.save()
