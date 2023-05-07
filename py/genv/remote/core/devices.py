from typing import Iterable, Tuple

from genv.entities import Devices

from .snapshot import exec, Config, Host


async def snapshot(config: Config) -> Tuple[Iterable[Host], Iterable[Devices]]:
    """
    Takes device snapshots on multiple hosts.

    :return: Returns the hosts that succeeded and their snapshots
    """
    return await exec(config, type="devices", sudo=False)
