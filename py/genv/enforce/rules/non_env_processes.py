from typing import Optional

from ...snapshot import Snapshot

from ..survey import Survey


def non_env_processes(
    snapshot: Snapshot, survey: Survey, prefix: Optional[str] = None
) -> None:
    """
    Terminates processes that are not running in environments.
    """
    for process in snapshot.processes:
        if process.eid is not None:
            continue

        print(
            f"{f'[{prefix}] ' if prefix else ''}"
            f"Process {process.pid} is not running in a GPU environment"
        )

        survey.terminate(process.pid)
