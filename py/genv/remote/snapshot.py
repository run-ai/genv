import json
from typing import Iterable, Optional, Tuple

from ..snapshot import Snapshot
from ..json_ import JSONDecoder

from .ssh import run, Host, Config, Command

# TODO(raz): should we support cases where 'sudo' is not an option?


async def exec(config: Config, *, type: Optional[str], sudo: bool):
    args = ["exec", "usage", "snapshot"]

    if type:
        args.append(f"--type {type}")

    command = Command(args, sudo)

    hosts, stdouts = await run(config, command)

    return hosts, [json.loads(stdout, cls=JSONDecoder) for stdout in stdouts]


async def snapshot(config: Config) -> Tuple[Iterable[Host], Iterable[Snapshot]]:
    """
    Takes usage snapshots on multiple hosts.

    :return: Returns the hosts that succeeded and their snapshots
    """
    return await exec(config, type=None, sudo=True)
