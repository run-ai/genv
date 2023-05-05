from genv.devices import snapshot as devices
from genv.envs import snapshot as envs
from genv.processes import snapshot as processes
from genv.entities.snapshot import Snapshot


async def snapshot() -> Snapshot:
    return Snapshot(
        processes=await processes(),
        envs=envs(),
        devices=devices(),
    )
