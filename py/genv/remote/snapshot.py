import asyncio
import json
from typing import Iterable, Optional, Tuple

from ..runners import SshRunner
from ..snapshot import Snapshot
from ..json_ import JSONDecoder

from .ssh import run, Host, Config, Command
from ..snapshot_mode import SnapshotMode
from genv.snapshot import snapshot as snapshot_


# TODO(raz): should we support cases where 'sudo' is not an option?


async def exec(config: Config, *, type: Optional[str], sudo: bool):
    args = ["exec", "usage", "snapshot"]

    if type:
        args.append(f"--type {type}")

    command = Command(args, sudo)

    hosts, stdouts = await run(config, command)

    return hosts, [json.loads(stdout, cls=JSONDecoder) for stdout in stdouts]


async def snapshot(config: Config, mode: SnapshotMode = SnapshotMode.Full) -> Tuple[Iterable[Host], Iterable[Snapshot]]:
    """
    Takes usage snapshots on multiple hosts.

    :return: Returns the hosts that succeeded and their snapshots
    """
    if mode == SnapshotMode.Full:
        return await exec(config, type=None, sudo=True)
    elif mode == SnapshotMode.Partial:
        async def _try_snapshot(host: Host) -> Optional[Snapshot]:
            """
            Tries to take a remote snapshot.
            """
            ssh_runner = SshRunner(host.hostname, host.timeout)

            try:
                return await snapshot_(mode, ssh_runner)
            except Exception as err:
                print(f"Failed get remote snapshot over SSH to {host.hostname} ({str(err)})")
                return None

        snapshots = await asyncio.gather(*(_try_snapshot(host) for host in config.hosts))

        hosts = [
            host
            for host, remote_snapshot in zip(config.hosts, snapshots)
            if remote_snapshot is not None
        ]
        snapshots_objs = [snapshot for snapshot in snapshots if snapshot is not None]

        return hosts, snapshots_objs
    else:
        raise ValueError(f"Invalid value for 'mode' ({mode})")
