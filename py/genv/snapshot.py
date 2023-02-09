from dataclasses import dataclass
from typing import Iterable

from . import processes as processes_
from . import envs as envs_
from . import devices as devices_


@dataclass
class Snapshot:
    processes: processes_.Snapshot
    envs: Iterable[envs_.Env]
    devices: Iterable[devices_.Device]

    def attached(self) -> Iterable[devices_.Device]:
        """
        Returns devices with attached environments.
        """
        return [device for device in self.devices if len(device.eids) > 0]

    def filter(self, username: str):
        """
        Filters a snapshot by username.

        :return: A new snapshot with information related only to the given username.
        """
        envs = [env for env in self.envs if env.username == username]
        eids = [env.eid for env in envs]

        processes = self.processes.filter(eids=eids)

        devices = [
            devices_.Device(
                index=device.index,
                eids=[eid for eid in eids if eid in device.eids],
            )
            for device in self.devices
        ]

        return Snapshot(processes=processes, envs=envs, devices=devices)


# NOTE(raz): this method is not atomic because it runs manager executables in the background.
# each manager locks its state file and for this reason the snapshot is not coherent by definition.
# this should be done oppositely, by locking a single lock and querying all state files altogether.
async def snapshot() -> Snapshot:
    return Snapshot(
        processes=await processes_.snapshot(),
        envs=envs_.snapshot(),
        devices=devices_.snapshot(),
    )
