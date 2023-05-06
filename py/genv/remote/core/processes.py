from typing import Iterable, Tuple

from genv.entities import Processes

from .snapshot import exec, Config, Host


async def snapshot(config: Config) -> Tuple[Iterable[Host], Iterable[Processes]]:
    """
    Takes process snapshots on multiple hosts.

    :return: Returns the hosts that succeeded and their snapshots
    """
    return await exec(config, type="processes", sudo=True)
