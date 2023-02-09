from dataclasses import dataclass

from . import processes as processes_
from . import envs as envs_
from . import devices as devices_


@dataclass
class Snapshot:
    processes: processes_.Snapshot
    envs: envs_.Snapshot
    devices: devices_.Snapshot

    def filter(self, username: str):
        """
        Filters a snapshot by username.

        :return: A new snapshot with information related only to the given username.
        """
        envs = self.envs.filter(username=username)

        return Snapshot(
            processes=self.processes.filter(eids=envs.eids),
            envs=envs,
            devices=self.devices.filter(eids=envs.eids),
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
