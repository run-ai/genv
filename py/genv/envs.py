import subprocess
from typing import Dict, Iterable, Optional


# NOTE(raz): This should be the layer that queries and controls the state of Genv regarding active environments.
# Currently, it relies on executing the environment manager executable of Genv, as this is where the logic is implemented.
# This however should be done oppositely.
# The entire logic that queries and controls envs.json should be implemented here, and the environment manager executable
# should use methods from here.
# It should take the Genv lock for the atomicity of the transaction, and print output as needed.
# The current architecture has an inherent potential deadlock because each manager locks a different lock, and might
# call the other manager.


def eids() -> Iterable[str]:
    """
    Returns the identifiers of all active environments.

    :return: Identifiers of all active environments.
    """
    return (
        subprocess.check_output("genv exec envs query --query eid", shell=True)
        .decode("utf-8")
        .splitlines()
    )


def names() -> Dict[str, Optional[str]]:
    """
    Returns the names of all active environments.

    :return: A mapping from environment identifier to its configured name or None if not configured.
    """
    names = {}
    for line in (
        subprocess.check_output(
            "genv exec envs query --query eid config.name", shell=True
        )
        .decode("utf-8")
        .splitlines()
    ):
        eid, name = line.split(",")
        names[eid] = name or None

    return names


def gpu_memory(eid: int) -> Optional[str]:
    """
    Returns the configured GPU memory of an environment.

    :param eid: Environment to query
    :return: The configured GPU memory or None if not configured
    """
    return (
        subprocess.check_output(
            f"genv exec envs query --eid {eid} --query config.gpu_memory", shell=True
        )
        .decode("utf-8")
        .strip()
        or None
    )
