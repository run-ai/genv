from dataclasses import dataclass
from typing import Iterable, Optional

from . import processes as processes_
from . import envs as envs_
from . import devices as devices_


@dataclass
class Snapshot:
    processes: processes_.Snapshot
    envs: envs_.Snapshot
    devices: devices_.Snapshot

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


# NOTE(raz): this method is not atomic because it runs manager executables in the background.
# each manager locks its state file and for this reason the snapshot is not coherent by definition.
# this should be done oppositely, by locking a single lock and querying all state files altogether.
async def snapshot() -> Snapshot:
    return Snapshot(
        processes=await processes_.snapshot(),
        envs=envs_.snapshot(),
        devices=devices_.snapshot(),
    )
