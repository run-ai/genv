from dataclasses import dataclass
from typing import Iterable

from . import processes
from . import envs
from . import devices


@dataclass
class Snapshot:
    processes: Iterable[processes.Process]
    envs: Iterable[envs.Env]
    devices: Iterable[devices.Device]


# NOTE(raz): this method is not atomic because it runs manager executables in the background.
# each manager locks its state file and for this reason the snapshot is not coherent by definition.
# this should be done oppositely, by locking a single lock and querying all state files altogether.
async def snapshot() -> Snapshot:
    return Snapshot(
        processes=await processes.snapshot(),
        envs=envs.snapshot(),
        devices=devices.snapshot(),
    )
