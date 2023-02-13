from typing import Iterable

from ....snapshot import Snapshot
from ....enforce import Survey, rules

from ...ssh import Host


def env_memory(
    hosts: Iterable[Host], snapshots: Iterable[Snapshot], surveys: Iterable[Survey]
) -> None:
    """
    Terminates remote processes from environments that exceed their memory capacity.
    """
    for host, snapshot, survey in zip(hosts, snapshots, surveys):
        rules.env_memory(snapshot, survey, prefix=host.hostname)
