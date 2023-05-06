from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Iterable, Optional

import genv.utils

from .env import Env


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

        return Envs(envs)

    def cleanup(
        self,
        *,
        poll_pid: Callable[[int], bool] = genv.utils.poll_pid,
        poll_kernel: Callable[[str], bool] = genv.utils.poll_jupyter_kernel,
    ):
        """
        Cleans up the collection in place.
        """
        for env in self.envs:
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
