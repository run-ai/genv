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


def get_env(process: dict, name: str) -> Optional[str]:
    """
    Returns the value of an environment variable if set.
    """

    for env in process["env"]:
        if env.startswith(f"{name}="):
            return env.split("=")[-1]


def append_env(process: dict, name: str, value: str) -> None:
    """
    Appends an environment variable to the configuration.
    """

    process["env"].append(f"{name}={value}")


def update_env(process: dict, name: str, mutator: Callable[[str], str]) -> None:
    """
    Updates an environment variable.
    """

    for index, env in enumerate(process["env"]):
        if env.startswith(f"{name}="):
            value = env.split("=")[-1]
            process["env"][index] = f"{name}={mutator(value)}"
            return

    raise RuntimeError(f"Cannot update environment variable '{name}'")


def update_process(process: dict, container_id: str) -> None:
    """Updates a process json object.

    References:
    - https://github.com/opencontainers/runtime-spec/blob/main/config.md#process
    """

    append_env(process, "GENV_CONTAINER", "1")

    if not get_env(process, "GENV_ACTIVATE") == "0":
        if not get_env(process, "GENV_ENVIRONMENT_ID"):
            # TODO(raz): consider generating an environment identifier which is different than
            # the container identifier to avoid this kind of information leak.
            # also note that a short version of the container identifier is set as the container
            # hostname then it might be ok.
            append_env(process, "GENV_ENVIRONMENT_ID", container_id)

    if not get_env(process, "GENV_MOUNT_SHIMS") == "0":
        update_env(process, "PATH", lambda value: f"/opt/genv/shims:{value}")


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

    update_process(config["process"], container_id)

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


def do_exec(process_json: str, container_id: str) -> None:
    """
    Performs the command 'exec'.
    """

    with open(process_json) as f:
        process = json.load(f)

    update_process(process, container_id)

    with open(process_json, "w") as f:
        json.dump(process, f)


# TODO(raz): prettify error messages
if __name__ == "__main__":
    if "create" in sys.argv:
        do_create(container_id=sys.argv[-1])
    elif "exec" in sys.argv:
        do_exec(
            process_json=sys.argv[sys.argv.index("--process") + 1],
            container_id=sys.argv[-1],
        )
    subprocess.check_call([find_container_runtime()] + sys.argv[1:])
