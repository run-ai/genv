from typing import Any, Optional, Union

import genv.utils
from genv.entities import Env, Envs
import genv.serialization

from .utils import File


class State(File[Envs]):
    def __init__(self, cleanup: bool = True, reset: bool = False) -> None:
        super().__init__(
            genv.utils.get_temp_file_path("envs.json"),
            cleanup,
            reset,
        )

    def _create(self):
        return Envs([])

    def _convert(self, o: Union[Any, Envs]) -> Envs:
        def _get_field(obj, field, cls, *args):
            return (
                getattr(obj, field, *args)
                if isinstance(obj, cls)
                else obj.get(field, *args)
            )

        def _get_env_field(env, field, *args):
            return _get_field(env, field, Env, *args)

        def _get_config_field(env, field, *args):
            config = _get_env_field(env, "config")

            return _get_field(config, field, Env.Config, *args)

        # the following logic converts state files from versions <= 0.9.0.
        # note that the indicator is 'o.envs' and not 'o' itself because the structure of
        # the state file from these versions was similar to the snapshot structure (a single
        # key named "envs") so the JSON decoder parsed the object as a snapshot object.
        if isinstance(o.envs, dict):
            o = Envs(
                [
                    Env(
                        _get_env_field(env, "eid"),
                        _get_env_field(env, "uid"),
                        _get_env_field(env, "creation"),
                        _get_env_field(env, "username", None),
                        Env.Config(
                            _get_config_field(env, "name", None),
                            _get_config_field(env, "gpu_memory", None),
                            _get_config_field(env, "gpus", None),
                        ),
                        _get_env_field(env, "pids", []),
                        _get_env_field(env, "kernel_ids", []),
                    )
                    for env in o.envs.values()
                ]
            )

        return o

    def _clean(self, envs: Envs) -> None:
        envs.cleanup()


def snapshot() -> Envs:
    """
    Returns an environments snapshot.
    """
    return State().load()


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
    with State() as envs:
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
    with State() as envs:
        env = envs[eid]

        env.config.name = name
        env.config.gpu_memory = gpu_memory
        env.config.gpus = gpus
