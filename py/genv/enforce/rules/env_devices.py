from typing import Optional

from ...snapshot import Snapshot

from ..survey import Survey


def env_devices(
    snapshot: Snapshot, survey: Survey, prefix: Optional[str] = None
) -> None:
    """
    Terminates processes on devices not attached to their environments.
    """
    for env in snapshot.envs:
        allowed = snapshot.devices.filter(eid=env.eid).indices

        for process in snapshot.processes.filter(eid=env.eid):
            unallowed = [index for index in process.indices if index not in allowed]

            if len(unallowed) == 0:
                continue

            print(
                f"{f'[{prefix}] ' if prefix else ''}"
                f"Process {process.pid} from environment {env.eid} is using non-attached GPU(s) {','.join([str(index) for index in unallowed])}"
            )

            survey.terminate(process.pid)
