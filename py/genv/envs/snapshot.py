from dataclasses import dataclass
from typing import Callable, Iterable, Optional

from genv.envs.env import Env
from genv import poll


@dataclass
class Snapshot:
    """
    A snapshot of active environments.
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
        creation: str,
        username: Optional[str],
    ) -> None:
        """
        Activates a new environment.
        """
        self.envs.append(
            Env(
                eid=eid,
                uid=uid,
                creation=creation,
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
        Returns a new filtered snapshot.

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

        return Snapshot(envs)

    def cleanup(
        self,
        *,
        poll_pid: Callable[[int], bool] = poll.poll_pid,
        poll_kernel: Callable[[str], bool] = poll.poll_jupyter_kernel,
    ):
        """
        Cleans up the snapshot in place.
        """
        for env in self.envs:
            env.cleanup(poll_pid=poll_pid, poll_kernel=poll_kernel)

        self.envs = [env for env in self.envs if env.active]
