from typing import Iterable, Tuple

from genv.processes.snapshot import Snapshot
from genv.remote.snapshot import exec, Config, Host


async def snapshot(config: Config) -> Tuple[Iterable[Host], Iterable[Snapshot]]:
    """
    Takes process snapshots on multiple hosts.

    :return: Returns the hosts that succeeded and their snapshots
    """
    return await exec(config, type="processes", sudo=True)
