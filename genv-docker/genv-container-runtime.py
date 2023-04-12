#!/usr/bin/env python3

import os
import shutil
import sys
import json
import subprocess
from typing import Callable, Iterable, Optional


def find_container_runtime() -> str:
    """
    Finds an available container runtime to execute.
    """

    for name in ["nvidia-container-runtime", "runc"]:
        path = shutil.which(name)
        if path:
            return path

    raise RuntimeError("Cannot find any container runtime")


def get_env(config: dict, name: str) -> Optional[str]:
    """
    Returns the value of an environment variable if set.
    """

    for env in config["process"]["env"]:
        if env.startswith(f"{name}="):
            return env.split("=")[-1]


def append_env(config: dict, name: str, value: str) -> None:
    """
    Appends an environment variable to the configuration.
    """

    config["process"]["env"].append(f"{name}={value}")


def update_env(config: dict, name: str, mutator: Callable[[str], str]) -> None:
    """
    Updates an environment variable.
    """

    for index, env in enumerate(config["process"]["env"]):
        if env.startswith(f"{name}="):
            value = env.split("=")[-1]
            config["process"]["env"][index] = f"{name}={mutator(value)}"
            return

    raise RuntimeError(f"Cannot update environment variable '{name}'")


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


def do_create(container_id: str) -> None:
    """
    Performs the command 'create'.
    """

    with open("config.json") as f:
        config = json.load(f)

    if not get_env(config, "GENV_ENVIRONMENT_ID"):
        # TODO(raz): consider generating an environment identifier which is different than
        # the container identifier to avoid this kind of information leak.
        # also note that a short version of the container identifier is set as the container
        # hostname then it might be ok.
        append_env(config, "GENV_ENVIRONMENT_ID", container_id)

    if not (get_env(config, "GENV_BYPASS") == "1"):
        # TODO(raz): make the shim-injection configurable using env var "GENV_BYPASS"
        update_env(config, "PATH", lambda value: f"/opt/genv/shims:{value}")

    # NOTE(raz): even though the hook "prestart" is deprecated, we are using it because the
    # nvidia container runtime still uses it itself and we need to make sure we will run before.
    append_hook(
        config,
        "prestart",
        os.path.join(os.path.dirname(__file__), "genv-container-runtime-hook.py"),
    )

    # TODO(raz): clean up environment on 'poststop'

    with open("config.json", "w") as f:
        json.dump(config, f)


if __name__ == "__main__":
    if "create" in sys.argv:
        do_create(container_id=sys.argv[-1])

    subprocess.check_call([find_container_runtime()] + sys.argv[1:])
