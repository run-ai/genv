import asyncio
from dataclasses import dataclass
from typing import Iterable, Optional, Dict
from datetime import datetime

from . import processes as processes_
from . import envs as envs_
from . import devices as devices_
from .runners import LocalRunner
from .runners import Runner


@dataclass
class Snapshot:
    processes: Iterable[processes_.Process] = None
    envs: Iterable[envs_.Env] = None
    devices: Iterable[devices_.Device] = None
    time: Optional[datetime] = None

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

        processes = [process for process in self.processes if process.eid in eids]

        devices = [
            devices_.Device(
                index=device.index,
                eids=[eid for eid in eids if eid in device.eids],
            )
            for device in self.devices
        ]

        return Snapshot(processes=processes, envs=envs, devices=devices)

    @staticmethod
    async def get_nvidia_smi_snapshot(host_runner: Runner) -> 'Snapshot':
        return Snapshot(devices=await devices_.nvidia_smi_snapshot(host_runner), time=datetime.now())


# NOTE(raz): this method is not atomic because it runs manager executables in the background.
# each manager locks its state file and for this reason the snapshot is not coherent by definition.
# this should be done oppositely, by locking a single lock and querying all state files altogether.
async def snapshot() -> Snapshot:
    return Snapshot(
        processes=await processes_.snapshot(LocalRunner()),
        envs=envs_.snapshot(),
        devices=devices_.snapshot(),
    )


async def nvidia_smi_snapshots(hosts_runners: Optional[Iterable[Runner]] = None) -> Dict[str, Snapshot]:
    if not hosts_runners:
        hosts_runners = [LocalRunner()]

    hosts_names = []
    remote_snapshots_calls = []
    for host_runner in hosts_runners:
        hosts_names.append(host_runner.name())
        remote_snapshots_calls.append(Snapshot.get_nvidia_smi_snapshot(host_runner))

    snapshots = await asyncio.gather(*remote_snapshots_calls)
    return dict(zip(hosts_names, snapshots))
