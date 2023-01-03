from dataclasses import dataclass
from typing import Iterable
import sys

import genv.nvidia_smi
import genv.os_
import genv.users

from .process import Process


@dataclass
class Snapshot:
    processes: Iterable[Process]
    user_attachments: genv.users.Attachments


# NOTE(raz): this method is not atomic because it runs manager executables in the background.
# each manager locks its state file and for this reason the snapshot is not coherent by definition.
# this should be done oppositely, by locking a single lock and querying all state files altogether.
async def take() -> Snapshot:
    """
    Takes a snapshot of the current state of the system.
    This includes running processes, active environments and device attachments.
    """
    processes = []

    for process in await genv.nvidia_smi.compute_processes():
        try:
            eid = genv.os_.get_process_environ(process.pid).get(
                "GENV_ENVIRONMENT_ID", None
            )

            process_ = Process(
                process.gpu_index,
                process.pid,
                process.used_gpu_memory,
                eid,
            )

            processes.append(process_)
        except PermissionError:
            print(
                f"[WARNING] Not enough permissions to query environment of process {process.pid}",
                file=sys.stderr,
            )
        except FileNotFoundError:
            print(f"[DEBUG] Process {process.pid} already terminated", file=sys.stderr)

    user_attachments = genv.users.attachments()

    return Snapshot(processes, user_attachments)
