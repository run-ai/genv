from dataclasses import dataclass
import subprocess
from typing import Dict, Iterable, Optional, Union

from genv.serialization.partial_deserialization import smart_ctor


# NOTE(raz): This should be the layer that queries and controls the state of Genv regarding active environments.
# Currently, it relies on executing the environment manager executable of Genv, as this is where the logic is implemented.
# This however should be done oppositely.
# The entire logic that queries and controls envs.json should be implemented here, and the environment manager executable
# should use methods from here.
# It should take the Genv lock for the atomicity of the transaction, and print output as needed.
# The current architecture has an inherent potential deadlock because each manager locks a different lock, and might
# call the other manager.


@dataclass
class Env:
    eid: str
    username: Optional[str]
    name: Optional[str]

    def __init__(self, *args_dict, **kwargs):
        smart_ctor(self, *args_dict, **kwargs)

    def __hash__(self) -> int:
        return self.eid.__hash__()


def snapshot() -> Iterable[Env]:
    return [
        Env(eid, username or None, name or None)
        for eid, username, name in query("eid", "username", "config.name")
    ]


def query(
    *properties: str, eid: Optional[str] = None, eids: bool = False
) -> Union[
    str,
    Iterable[str],
    Iterable[Iterable[str]],
    Dict[str, str],
    Dict[str, Iterable[str]],
]:
    """
    Queries the environment manager about all active environments or a specific one.
    Returns a query result per environment.
    A query result can be a single string if only a single property was queried,
    or a list of strings if multiple properties were queried.

    :param properties: Environment properties to query
    :param eid: Identifier of a specific environment to query
    :param eids: Return a mapping between environment identifiers to query results
    """
    if len(properties) == 0:
        raise RuntimeError("At least one query property must be provided")

    command = "genv exec envs query"

    if eid:
        command = f"{command} --eid {eid}"
    else:
        properties = ("eid", *properties)

    command = f"{command} --query {' '.join(properties)}"

    output = subprocess.check_output(command, shell=True).decode("utf-8").strip()

    if eid:
        return output if len(properties) == 1 else output.split(",")
    else:
        result = dict()

        for line in output.splitlines():
            eid, line = line.split(",", 1)
            result[eid] = line if (len(properties) - 1) == 1 else line.split(",")

        return result if eids else list(result.values())


def eids() -> Iterable[str]:
    """
    Returns the identifiers of all active environments.

    :return: Identifiers of all active environments.
    """
    return query("eid")


def names() -> Dict[str, Optional[str]]:
    """
    Returns the names of all active environments.

    :return: A mapping from environment identifier to its configured name or None if not configured.
    """
    return {
        eid: (name or None) for eid, name in query("config.name", eids=True).items()
    }


def gpu_memory(eid: str) -> Optional[str]:
    """
    Returns the configured amount of GPU memory of an environment.

    :param eid: Environment to query
    :return: The configured amount of GPU memory or None if not configured
    """
    return query("config.gpu_memory", eid=eid) or None
