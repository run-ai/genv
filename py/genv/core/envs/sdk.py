from typing import Optional

from genv.entities import Envs

from .file import load, mutate


def activate(
    eid: str,
    uid: int,
    username: Optional[str] = None,
    *,
    pid: Optional[int] = None,
    kernel_id: Optional[str] = None,
) -> None:
    """
    Activates an environment if does not exist and attaches a proces or a Jupyter kernel to it.
    """
    with mutate() as envs:
        if eid not in envs:
            envs.activate(
                eid=eid,
                uid=uid,
                username=username,
            )

        envs[eid].attach(pid=pid, kernel_id=kernel_id)


def configure(
    eid: str,
    *,
    name: Optional[str] = None,
    gpu_memory: Optional[str] = None,
    gpus: Optional[int] = None,
) -> None:
    """
    Configures an environment.
    """
    with mutate() as envs:
        env = envs[eid]

        env.config.name = name
        env.config.gpu_memory = gpu_memory
        env.config.gpus = gpus


def snapshot() -> Envs:
    """
    Returns an environments snapshot.
    """
    return load()
