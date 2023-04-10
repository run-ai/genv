#!/usr/bin/env python3

import os
from subprocess import CalledProcessError
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

# NOTE(raz): we need to set $PATH only because the implementation of genv.envs is currently
# based on running Genv executables (i.e. genv-envs) in subprocesses.
# once the architecture will be reveresed, the Python package would be enough and this would
# no longer be unnecessary.
os.environ["PATH"] = f"{os.path.join(GENV_ROOT, 'bin')}:{os.environ['PATH']}"

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


if __name__ == "__main__":
    state = json.load(sys.stdin)

    with open("config.json") as f:
        config = json.load(f)

    eid = get_env(config, "GENV_ENVIRONMENT_ID", check=True)
    pid = state["pid"]

    # NOTE(raz): this de-facto would always be uid 0 (root).
    # we should think if we want to:
    # 1. use the uid of the container (https://github.com/opencontainers/runtime-spec/blob/main/config.md#posix-platform-user)
    # 2. use the uid of the user that ran the 'docker run' command (using some environment variable injected by genv-docker)
    # 3. make uid optional for environments
    uid = os.getuid()

    genv.envs.activate(eid, uid, pid)

    gpus = get_env(config, "GENV_GPUS")
    gpu_memory = get_env(config, "GENV_GPU_MEMORY")

    if gpu_memory:
        # NOTE(raz): this must happen before attaching in order to take effect
        genv.envs.configure(eid, "gpu-memory", gpu_memory)

    if gpus:
        genv.envs.configure(eid, "gpus", gpus)

        try:  # this could fail if for example there are no available devices
            indices = genv.devices.attach(eid, gpus)
        except CalledProcessError as e:
            print(e.stdout, file=sys.stderr)
            exit(1)

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

        with open("config.json", "w") as f:
            json.dump(config, f)
