from typing import Iterable

from ....snapshot import Snapshot
from ....enforce import Survey, rules

from ...ssh import Host


def non_env_processes(
    hosts: Iterable[Host], snapshots: Iterable[Snapshot], surveys: Iterable[Survey]
) -> None:
    """
    Terminates remote processes that are not running in environments.
    """
    for host, snapshot, survey in zip(hosts, snapshots, surveys):
        rules.non_env_processes(snapshot, survey, prefix=host.hostname)
