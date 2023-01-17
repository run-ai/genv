import json
from typing import Iterable

from .. import run_on_hosts_ssh
from ..snapshot import Snapshot
from genv.serialization.json_ import JSONDecoder

snapshot_command = ["genv", "exec", "usage", "snapshot"]


async def snapshot(hosts: Iterable[str], root: str) -> Iterable[Snapshot]:
    """
    Takes usage snapshots on multiple hosts.
    """
    stdouts = await run_on_hosts_ssh(hosts, *snapshot_command, process_env={"PATH": f'"{root}/bin:$PATH"'}, sudo=True)

    return [json.loads(stdout, cls=JSONDecoder) for stdout in stdouts]
