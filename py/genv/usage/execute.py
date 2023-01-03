import sys
from typing import Optional, Set, Tuple

import genv.devices
import genv.os_

from .report import Report, Process


def _terminate(processes: Set[Process]) -> None:
    for process in processes:
        try:
            print(
                f"Terminating process {process.pid} from environment {process.eid or 'N/A'} that is running on GPU {process.gpu_index} and using {process.used_gpu_memory}"
            )

            genv.os_.terminate(process.pid)
        except PermissionError:
            print(
                f"[ERROR] Not enough permissions to terminate process {process.pid}",
                file=sys.stderr,
            )
        except ProcessLookupError:
            print(f"[DEBUG] Process {process.pid} already terminated", file=sys.stderr)


def _detach(envs: Set[Tuple[str, int, Optional[str]]]) -> None:
    for eid, index, username in envs:
        print(
            f"Detaching environment {eid} of user {username or 'N/A'} from device {index}"
        )

        genv.devices.detach(eid, index)


def execute(report: Report) -> None:
    """
    Terminates processes and detaches environments from devices according to the given report.
    """
    _terminate(report.processes_to_terminate)
    _detach(report.envs_to_detach)
