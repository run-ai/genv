import json
from typing import Iterable

from ..snapshot import Snapshot
from genv.serialization.json_ import JSONDecoder

from .ssh import run


async def snapshot(hosts: Iterable[str], root: str) -> Iterable[Snapshot]:
    """
    Takes usage snapshots on multiple hosts.
    """
    stdouts = await run(
        hosts,
        root,
        "exec",
        "usage",
        "snapshot",
        sudo=True,
    )

    return [json.loads(stdout, cls=JSONDecoder) for stdout in stdouts]
