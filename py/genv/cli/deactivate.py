import argparse

import genv.utils
import genv.core
import genv.sdk


def add_arguments(parser: argparse.ArgumentParser) -> None:
    """
    Adds "genv deactivate" arguments to a parser.
    """

    pass


def run(shell: int, args: argparse.Namespace) -> None:
    """
    Runs the "genv deactivate" logic.
    """

    if not genv.sdk.active():
        raise RuntimeError("Not running in an active environment")

    with genv.utils.global_lock():
        genv.core.envs.deactivate(pid=shell)

        # clean up devices in case this environment had attached devices and this
        # is the last terminal from the environment
        genv.core.devices.cleanup()

    print(
        f"""
_genv_unset_envs
_genv_restore_envs
"""
    )
