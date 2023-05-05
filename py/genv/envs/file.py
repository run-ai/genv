from contextlib import contextmanager
from typing import Any, Union

from genv import json_
from genv import utils
from genv.entities.envs import Env, Envs


_PATH = utils.get_temp_file_path("envs.json")


def _creator() -> Envs:
    """
    Creates an empty state.
    """
    return Envs([])


def _converter(o: Union[Envs, Any]) -> Envs:
    """
    Converts the loaded object if needed.
    """
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


def _cleaner(envs: Envs) -> None:
    """
    Cleans up inactive environments.
    """
    envs.cleanup()


def load(cleanup: bool = True, reset: bool = False) -> Envs:
    """
    Loads from disk.
    """
    return utils.load_state(
        _PATH,
        creator=_creator,
        cleaner=_cleaner,
        converter=_converter,
        json_decoder=json_.JSONDecoder,
        cleanup=cleanup,
        reset=reset,
    )


def save(snapshot: Envs) -> None:
    """
    Saves to disk.
    """
    utils.save_state(
        snapshot,
        _PATH,
        json_encoder=json_.JSONEncoder,
    )


@contextmanager
def mutate(cleanup: bool = True, reset: bool = False) -> Envs:
    """
    Mutates state on disk.
    """
    envs = load(cleanup, reset)

    yield envs

    save(envs)