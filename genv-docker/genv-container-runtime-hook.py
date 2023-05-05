#!/usr/bin/env python3

import os
from pathlib import Path
import subprocess
import sys
import json
from typing import Optional

GENV_ROOT = os.path.realpath(
    os.environ.get("GENV_ROOT", os.path.join(os.path.dirname(__file__), ".."))
)

# NOTE(raz): we manually set the system path because becase the Genv Python package is not
# guaranteed to be installed.
# once it will be installed, we could remove this.
sys.path.append(os.path.join(GENV_ROOT, "py"))

import genv


def get_env(config: dict, name: str, *, check: bool = False) -> Optional[str]:
    """
    Returns the value of an environment variable if set.
    """

    for env in config["process"]["env"]:
        if env.startswith(f"{name}="):
            return env.split("=")[-1]

    if check:
        raise RuntimeError(f"Cannot find the environment variable '{name}'")


def activate_environment(state: dict, eid: str):
    """
    Activates an environment for the container.
    """

    pid = state["pid"]

    # NOTE(raz): this de-facto would always be uid 0 (root).
    # we should think if we want to:
    # 1. use the uid of the container (https://github.com/opencontainers/runtime-spec/blob/main/config.md#posix-platform-user)
    # 2. use the uid of the user that ran the 'docker run' command (using some environment variable injected by genv-docker)
    # 3. make uid optional for environments
    uid = os.getuid()

    genv.envs.activate(eid, uid, pid=pid)


def configure_environment(config: dict, eid: str):
    """
    Configures the environment.
    """
    gpu_memory = get_env(config, "GENV_GPU_MEMORY")
    gpus = get_env(config, "GENV_GPUS")

    genv.envs.configure(
        eid,
        gpu_memory=gpu_memory,
        gpus=int(gpus) if gpus else None,
    )


def attach_environment(config: dict, eid: str):
    """
    Attaches the environment to devices.
    """

    indices = genv.devices.attach(eid)

    # NOTE(raz): setting environment variables here will not have effect on the process
    # environment as it is now too late in the container lifecycle.
    # however, the nvidia container runtime hook, that will run after us, will respect this
    # environment variable from the configuration.
    #
    # p.s. we saw that de-facto the last value is the one that matters.
    # so appending "NVIDIA_VISIBLE_DEVICES" works even if it is already set.
    config["process"]["env"].append(
        f"NVIDIA_VISIBLE_DEVICES={','.join(str(index) for index in indices)}"
    )


def mount_shims(state: dict, config: dict):
    """
    Mounts shims into the container.
    """

    # inspired by https://github.com/NVIDIA/libnvidia-container/blob/v1.13.0/src/nvc_mount.c#L99-L151
    # TODO(raz): the file and directory are not created with the correct uid and gid.

    container_root = config["root"]["path"]
    container_genv = f"{container_root}/opt/genv"
    container_shims = f"{container_genv}/shims"

    host_genv = GENV_ROOT
    host_shims = f"{host_genv}/shims"

    Path(container_shims).mkdir(mode=0o755, parents=True, exist_ok=True)

    for shim in ["nvidia-smi"]:
        host_shim = f"{host_shims}/{shim}"
        container_shim = f"{container_shims}/{shim}"

        Path(container_shim).touch(mode=0o755, exist_ok=True)

        # TODO(raz): can we do the following without shells and subprocesses?

        subprocess.check_call(
            f"nsenter --mount --target {state['pid']} mount --bind {host_shim} {container_shim}",
            shell=True,
        )
        subprocess.check_call(
            f"nsenter --mount --target {state['pid']} mount --bind -o remount,ro,nosuid {container_shim}",
            shell=True,
        )


# TODO(raz): prettify error messages
if __name__ == "__main__":
    state = json.load(sys.stdin)

    # TODO(raz): is it ok to assume that the current working directory is the bundle
    # or should we respect state["bundle"]?
    with open("config.json") as f:
        config = json.load(f)

    if not get_env(config, "GENV_ACTIVATE") == "0":
        eid = get_env(config, "GENV_ENVIRONMENT_ID", check=True)

        with genv.utils.global_lock():
            activate_environment(state, eid)
            configure_environment(config, eid)

            if not get_env(config, "GENV_ATTACH") == "0":
                attach_environment(config, eid)

    if not get_env(config, "GENV_MOUNT_SHIMS") == "0":
        mount_shims(state, config)

    with open("config.json", "w") as f:
        json.dump(config, f)
