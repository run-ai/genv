import json
from typing import Iterable, Tuple

from ..snapshot import Snapshot
from ..json_ import JSONDecoder

from .ssh import run, Host, Config, Command


async def snapshot(config: Config) -> Tuple[Iterable[Host], Iterable[Snapshot]]:
    """
    Takes usage snapshots on multiple hosts.

    :return: Returns the hosts that succeeded and their snapshots
    """
    command = Command(["exec", "usage", "snapshot"], sudo=True)

    hosts, stdouts = await run(config, command)

    return hosts, [json.loads(stdout, cls=JSONDecoder) for stdout in stdouts]
