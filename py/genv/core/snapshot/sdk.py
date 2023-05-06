from genv.entities.snapshot import Snapshot

from genv.core.envs import snapshot as envs
from genv.core.devices import snapshot as devices
from genv.core.processes import snapshot as processes


async def snapshot() -> Snapshot:
    return Snapshot(
        processes=await processes(),
        envs=envs(),
        devices=devices(),
    )
