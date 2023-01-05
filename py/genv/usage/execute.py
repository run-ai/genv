import sys
from typing import Iterable, Tuple

import genv.devices
import genv.os_

from .envs import Env
from .processes import Process
from .report import Report


def _terminate(processes: Iterable[Process]) -> None:
    for process in processes:
        try:
            print(
                f"Terminating process {process.pid} from environment {process.eid or 'N/A'} that is running on GPU(s) {','.join([str(usage.index) for usage in process.used_gpu_memory])}"
            )

            genv.os_.terminate(process.pid)
        except PermissionError:
            print(
                f"[ERROR] Not enough permissions to terminate process {process.pid}",
                file=sys.stderr,
            )
        except ProcessLookupError:
            print(f"[DEBUG] Process {process.pid} already terminated", file=sys.stderr)


def _detach(envs: Iterable[Tuple[Env, int]]) -> None:
    for env, index in envs:
        print(
            f"Detaching environment {env.eid} of user {env.username or 'N/A'} from device {index}"
        )

        genv.devices.detach(env.eid, index)


def execute(report: Report) -> None:
    """
    Terminates processes and detaches environments from devices according to the given report.
    """
    _terminate(report.processes_to_terminate)
    _detach(report.envs_to_detach)
