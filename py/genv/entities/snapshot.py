from dataclasses import dataclass
from typing import Iterable, Optional

from .devices import Devices
from .envs import Envs
from .processes import Processes


@dataclass
class Snapshot:
    processes: Processes
    envs: Envs
    devices: Devices

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
        envs = self.envs.filter(deep=deep, eid=eid, eids=eids, username=username)

        return Snapshot(
            processes=self.processes.filter(deep=deep, eids=envs.eids),
            envs=envs,
            devices=self.devices.filter(deep=deep, eids=envs.eids),
        )
