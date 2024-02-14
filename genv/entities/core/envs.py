from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Iterable, Optional, Type, Union

import genv.utils


@dataclass
class Env:
    @dataclass
    class Config:
        name: Optional[str] = None
        gpu_memory: Optional[str] = None
        gpus: Optional[int] = None

        def load(self, path: Union[str, Path]) -> None:
            """Loads from disk"""

            def _load_field(basename: str, type: Type = str) -> None:
                file = Path(path).joinpath(basename)

                if file.is_file():
                    return type(file.read_text().strip())

            self.name = _load_field("name")
            self.gpu_memory = _load_field("gpu-memory")
            self.gpus = _load_field("gpus", int)

        def save(self, path: Union[str, Path]) -> None:
            """Saves to disk"""

            def _save_field(basename: str, value: Optional[Any]) -> None:
                file = Path(path).joinpath(basename)

                if value is not None:
                    file.write_text(str(value))
                else:
                    file.unlink(missing_ok=True)

            _save_field("name", self.name)
            _save_field("gpu-memory", self.gpu_memory)
            _save_field("gpus", self.gpus)

    eid: str
    uid: int
    creation: str
    username: Optional[str]
    config: Config
    pids: Iterable[int]
    kernel_ids: Iterable[str]

    @property
    def time_since(self) -> str:
        return genv.utils.time_since(self.creation)

    @property
    def active(self) -> bool:
        return len(self.pids) > 0 or len(self.kernel_ids) > 0

    def __hash__(self) -> int:
        return self.eid.__hash__()

    def cleanup(
        self,
        *,
        poll_pid: Callable[[int], bool] = None,
        poll_kernel: Callable[[str], bool] = None,
    ):
        """
        Cleans up in place.
        """
        if poll_pid is not None:
            self.pids = [pid for pid in self.pids if poll_pid(pid)]

        if poll_kernel is not None:
            self.kernel_ids = [
                kernel_id for kernel_id in self.kernel_ids if poll_kernel(kernel_id)
            ]

    def attach(
        self, *, pid: Optional[int] = None, kernel_id: Optional[str] = None
    ) -> None:
        """
        Attaches a process or a Jupyter kernel to an environment.
        """
        if pid is not None:
            self.pids.append(pid)

        if kernel_id is not None:
            self.kernel_ids.append(kernel_id)


@dataclass
class Envs:
    """
    A collection of environments.
    """

    envs: Iterable[Env]

    @property
    def eids(self) -> Iterable[str]:
        return [env.eid for env in self.envs]

    @property
    def usernames(self) -> Iterable[str]:
        return set(env.username for env in self.envs if env.username)

    def __iter__(self):
        return self.envs.__iter__()

    def __len__(self):
        return self.envs.__len__()

    def __getitem__(self, eid: str) -> Env:
        return next(env for env in self.envs if env.eid == eid)

    def __contains__(self, eid: str) -> bool:
        return any(env.eid == eid for env in self.envs)

    def activate(
        self,
        eid: str,
        uid: int,
        username: Optional[str] = None,
    ) -> None:
        """
        Activates a new environment.
        """
        self.envs.append(
            Env(
                eid=eid,
                uid=uid,
                creation=datetime.now().strftime(genv.utils.DATETIME_FMT),
                username=username,
                config=Env.Config(name=None, gpu_memory=None, gpus=None),
                pids=[],
                kernel_ids=[],
            )
        )

    def filter(
        self,
        deep: bool = True,
        *,
        eid: Optional[str] = None,
        eids: Optional[Iterable[str]] = None,
        username: Optional[str] = None,
        name: Optional[str] = None,
    ):
        """
        Returns a new filtered collection.

        :param deep: Perform deep filtering
        :param eid: Environment identifier to keep
        :param eids: Environment identifiers to keep
        :param username: Username to keep
        """
        if eids:
            eids = set(eids)

        if eid:
            if not eids:
                eids = set()

            eids.add(eid)

        envs = self.envs

        if eids is not None:
            envs = [env for env in envs if env.eid in eids]

        if username is not None:
            envs = [env for env in envs if env.username == username]

        if name is not None:
            envs = [env for env in envs if env.config.name == name]

        return Envs(envs)

    def cleanup(
        self,
        *,
        eid: Optional[str] = None,
        eids: Optional[Iterable[str]] = None,
        poll_pid: Callable[[int], bool] = None,
        poll_kernel: Callable[[str], bool] = None,
    ):
        """Cleans up the collection in place.

        Cleans only the specified environments when passing identifiers.
        """
        if eids:
            eids = set(eids)

        if eid:
            if not eids:
                eids = set()

            eids.add(eid)

        for env in self.envs:
            if eids is not None:
                if env.eid not in eids:
                    continue

            env.cleanup(poll_pid=poll_pid, poll_kernel=poll_kernel)

        self.envs = [env for env in self.envs if env.active]

    def find(
        self, *, pid: Optional[int] = None, kernel_id: Optional[str] = None
    ) -> Iterable[Env]:
        """
        Returns the environments of the given process or kernel.
        """

        def _pred(env: Env) -> bool:
            if (pid is not None) and (pid in env.pids):
                return True

            if (kernel_id is not None) and (kernel_id in env.kernel_ids):
                return True

            return False

        return [env for env in self.envs if _pred(env)]
