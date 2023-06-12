import argparse

import genv.sdk


def add_arguments(parser: argparse.ArgumentParser) -> None:
    """
    Adds "genv status" arguments to a parser.
    """

    pass


def run(args: argparse.Namespace) -> None:
    """
    Runs the "genv status" logic.
    """

    if not genv.sdk.active():
        print("Environment is not active")
    else:
        print(f"Environment is active ({genv.sdk.eid()})")

        indices = genv.sdk.attached()

        if not indices:
            print("Detached from GPUs")
        else:
            print(f"Attached to GPUs at indices {','.join(map(str, indices))}")

        config = genv.sdk.configuration()

        print()
        print("Configuration")
        print(f"    Name: {config.name or 'N/A'}")
        print(f"    Device count: {config.gpus or 'N/A'}")
        print(f"    GPU memory capacity: {config.gpu_memory or 'N/A'}")
        print()
