import asyncio
import os
from typing import Dict, Iterable


async def run(*args: str) -> str:
    """
    Runs nvidia-smi with the given arguments as a subprocess, waits for it and returns its output.
    Raises 'RuntimeError' if subprocess exited with failure.
    """
    args = ["nvidia-smi", *args]

    process = await asyncio.create_subprocess_exec(
        *args,
        env={"GENV_BYPASS": "1", **os.environ},
        stdin=asyncio.subprocess.DEVNULL,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        command = " ".join(args)
        raise RuntimeError(
            f"Failed running '{command}' ({stderr.decode('utf-8').strip()})"
        )

    return stdout.decode("utf-8").strip()


async def device_uuids() -> Dict[str, int]:
    """
    Queries device UUIDs.

    :return: A mapping from device UUID to its index
    """
    output = await run("--query-gpu=uuid,index", "--format=csv,noheader")

    mapping = dict()

    for line in output.splitlines():
        uuid, index = line.split(", ")
        mapping[uuid] = int(index)

    return mapping


async def compute_apps() -> Iterable[Dict]:
    """
    Queries the running compute apps.
    """
    output = await run(
        "--query-compute-apps=gpu_uuid,pid,used_gpu_memory",
        "--format=csv,noheader,nounits",
    )

    apps = []

    for line in output.splitlines():
        gpu_uuid, pid, used_gpu_memory = line.split(", ")

        apps.append(
            dict(
                gpu_uuid=gpu_uuid, pid=int(pid), used_gpu_memory=f"{used_gpu_memory}mi"
            )
        )

    return apps
