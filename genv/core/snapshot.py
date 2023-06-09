from genv.entities import Snapshot

import genv.core.envs
import genv.core.devices
import genv.core.processes


async def snapshot() -> Snapshot:
    """
    Returns a full system snapshot.
    """

    processes = await genv.core.processes.snapshot()
    envs = genv.core.envs.snapshot()
    devices = genv.core.devices.snapshot()

    return Snapshot(processes, envs, devices)
