import json
from typing import Iterable

import genv.usage

from ..ssh import run_on_hosts


async def snapshot(hosts: Iterable[str], root: str) -> Iterable[genv.usage.Snapshot]:
    """
    Takes usage snapshots on multiple hosts.
    """
    stdouts = await run_on_hosts(
        hosts,
        root,
        "exec",
        "usage",
        "snapshot",
        sudo=True,
    )

    return [json.loads(stdout, cls=genv.usage.JSONDecoder) for stdout in stdouts]
