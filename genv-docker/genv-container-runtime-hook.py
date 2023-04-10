#!/usr/bin/env python3

import os
import sys
import json

GENV_ROOT = os.path.realpath(
    os.environ.get("GENV_ROOT", os.path.join(os.path.dirname(__file__), ".."))
)

# NOTE(raz): we manually set the system path because becase the Genv Python package is not
# guaranteed to be installed.
# once it will be installed, we could remove this.
sys.path.append(os.path.join(GENV_ROOT, "py"))

import genv


def find_environment_id(config: dict) -> str:
    """
    Finds the environment identifier of the container from the configuratoin.
    """

    for env in config["process"]["env"]:
        if env.startswith("GENV_ENVIRONMENT_ID="):
            return env.split("=")[-1]

    raise RuntimeError("Cannot find the environment identifier")


def activate_environment(eid: str, pid: int) -> None:
    """
    Registers the container as an active GPU environment in Genv.
    """

    # NOTE(raz): this de-facto would always be uid 0 (root).
    # we should think if we want to:
    # 1. use the uid of the container (https://github.com/opencontainers/runtime-spec/blob/main/config.md#posix-platform-user)
    # 2. use the uid of the user that ran the 'docker run' command (using some environment variable injected by genv-docker)
    # 3. make uid optional in the environment registry
    uid = os.getuid()

    # NOTE(raz): we need to set $PATH only because the implementation of genv.envs is currently
    # based on running Genv executables (i.e. genv-envs) in subprocesses.
    # once the architecture will be reveresed, the Python package would be enough and this would
    # be unnecessary.
    os.environ["PATH"] = f"{os.path.join(GENV_ROOT, 'bin')}:{os.environ['PATH']}"

    genv.envs.activate(eid, uid, pid)


if __name__ == "__main__":
    state = json.load(sys.stdin)

    with open("config.json") as f:
        config = json.load(f)

    eid = find_environment_id(config)
    pid = state["pid"]

    activate_environment(eid, pid)
