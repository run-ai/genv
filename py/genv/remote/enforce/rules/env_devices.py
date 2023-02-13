from typing import Iterable

from ....snapshot import Snapshot
from ....enforce import Survey, rules

from ...ssh import Host


def env_devices(
    hosts: Iterable[Host], snapshots: Iterable[Snapshot], surveys: Iterable[Survey]
) -> None:
    """
    Terminates remote processes on devices not attached to their environments.
    """
    for host, snapshot, survey in zip(hosts, snapshots, surveys):
        rules.env_devices(snapshot, survey, prefix=host.hostname)
