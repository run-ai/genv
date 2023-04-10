#!/usr/bin/env python3

from contextlib import contextmanager
import os
import shutil
import sys
import json
import subprocess
from typing import Iterable, Optional


def find_container_runtime() -> str:
    """
    Finds an available container runtime to execute.
    """

    for name in ["nvidia-container-runtime", "runc"]:
        path = shutil.which(name)
        if path:
            return path

    raise RuntimeError("Cannot find any container runtime")


@contextmanager
def mutate_config() -> dict:
    """
    A context manager for mutating the configuration.
    """

    with open("config.json") as f:
        config = json.load(f)

    yield config

    with open("config.json", "w") as f:
        json.dump(config, f)


def append_env(config: dict, name: str, value: str) -> None:
    """
    Appends an environment variable to the configuration.
    """

    config["process"]["env"].append(f"{name}={value}")


def append_hook(
    config: dict,
    type: str,
    path: str,
    *,
    args: Optional[Iterable[str]] = None,
    env: Optional[Iterable[str]] = None,
) -> None:
    """
    Appends a hook of the given type to the configuration.
    """

    hook = {"path": path}

    if args:
        hook["args"] = [path] + list(args)

    if env:
        hook["env"] = env

    if not "hooks" in config:
        config["hooks"] = {}

    hooks = config["hooks"]

    if not type in hooks:
        hooks[type] = []

    hooks[type].append(hook)


def create(environment_id: str) -> None:
    """
    Performs the command 'create'.
    """

    with mutate_config() as config:
        append_env(config, "GENV_ENVIRONMENT_ID", environment_id)

        append_hook(
            config,
            "createRuntime",
            os.path.join(os.path.dirname(__file__), "genv-container-runtime-hook.py"),
        )

        # TODO(raz): clean up environment on 'poststop'


if __name__ == "__main__":
    if "create" in sys.argv:
        container_id = sys.argv[-1]

        # TODO(raz): consider generating an environment identifier which is different than
        # the container identifier to avoid this kind of information leak.
        # also note that a short version of the container identifier is set as the container
        # hostname then it might be ok.
        environment_id = container_id

        create(environment_id)

    subprocess.check_call([find_container_runtime()] + sys.argv[1:])
