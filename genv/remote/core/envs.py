from typing import Iterable, Tuple

from genv.entities import Envs

from .snapshot import exec, Config, Host


async def snapshot(config: Config) -> Tuple[Iterable[Host], Iterable[Envs]]:
    """
    Takes environment snapshots on multiple hosts.

    :return: Returns the hosts that succeeded and their snapshots
    """
    return await exec(config, type="envs", sudo=False)
