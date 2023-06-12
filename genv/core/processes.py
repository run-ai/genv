import asyncio

from genv.entities import Process, Processes

import genv.utils.nvidia_smi


async def snapshot() -> Processes:
    """
    Returns a snapshot of all running compute processes.
    """
    uuids, apps = await asyncio.gather(
        genv.utils.nvidia_smi.device_uuids(), genv.utils.nvidia_smi.compute_apps()
    )

    pid_to_apps = {
        pid: [app for app in apps if app["pid"] == pid]
        for pid in set(app["pid"] for app in apps)
    }

    return Processes(
        [
            Process(
                pid=pid,
                used_gpu_memory=[
                    Process.Usage(
                        index=uuids[app["gpu_uuid"]], gpu_memory=app["used_gpu_memory"]
                    )
                    for app in apps
                ],
                eid=Process.eid(pid),
            )
            for pid, apps in pid_to_apps.items()
        ]
    )
