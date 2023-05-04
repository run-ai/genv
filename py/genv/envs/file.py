import os
from typing import Any, Union

from genv import json_
from genv import utils
from genv.envs.env import Env
from genv.envs.snapshot import Snapshot

PATH = utils.get_temp_file_path("envs.json")


def _convert(o: Union[Snapshot, Any]) -> Snapshot:
    """
    Converts the loaded state object to a snapshot if it not already is.
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
        o = Snapshot(
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


def load(reset: bool = False) -> Snapshot:
    """
    Loads from disk.
    """
    if os.path.exists(PATH) and not reset:
        return utils.load_state(
            PATH,
            convert=_convert,
            json_decoder=json_.JSONDecoder,
        )

    return Snapshot([])


def save(snapshot: Snapshot) -> None:
    """
    Saves to disk.
    """
    utils.save_state(
        snapshot,
        PATH,
        json_encoder=json_.JSONEncoder,
    )
