from typing import Iterable, Tuple

from genv.devices.snapshot import Snapshot
from genv.remote.snapshot import exec, Config, Host


async def snapshot(config: Config) -> Tuple[Iterable[Host], Iterable[Snapshot]]:
    """
    Takes device snapshots on multiple hosts.

    :return: Returns the hosts that succeeded and their snapshots
    """
    return await exec(config, type="devices", sudo=False)
