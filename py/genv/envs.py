from dataclasses import dataclass
import subprocess
from typing import Any, Dict, Iterable, Optional, Union

from . import utils

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
    uid: int
    creation: str
    username: Optional[str]

    @dataclass
    class Config:
        name: Optional[str]
        gpu_memory: Optional[str]

    config: Config

    @property
    def time_since(self) -> str:
        return utils.time_since(self.creation)

    def __hash__(self) -> int:
        return self.eid.__hash__()


@dataclass
class Snapshot:
    """
    A snapshot of active environments.
    """

    envs: Iterable[Env]

    @property
    def eids(self) -> Iterable[str]:
        return [env.eid for env in self.envs]

    @property
    def usernames(self) -> Iterable[str]:
        return set(env.username for env in self.envs if env.username)

    def __iter__(self):
        return self.envs.__iter__()

    def __len__(self):
        return self.envs.__len__()

    def __getitem__(self, eid: str) -> Env:
        return next(env for env in self.envs if env.eid == eid)

    def filter(
        self,
        deep: bool = True,
        *,
        eid: Optional[str] = None,
        eids: Optional[Iterable[str]] = None,
        username: Optional[str] = None,
    ):
        """
        Returns a new filtered snapshot.

        :param deep: Perform deep filtering
        :param eid: Environment identifier to keep
        :param eids: Environment identifiers to keep
        :param username: Username to keep
        """
        if eids:
            eids = set(eids)

        if eid:
            if not eids:
                eids = set()

            eids.add(eid)

        envs = self.envs

        if eids is not None:
            envs = [env for env in envs if env.eid in eids]

        if username is not None:
            envs = [env for env in envs if env.username == username]

        return Snapshot(envs)


def snapshot() -> Snapshot:
    return Snapshot(
        [
            Env(
                eid,
                int(uid),
                creation,
                username or None,
                Env.Config(name or None, gpu_memory or None),
            )
            for eid, uid, creation, username, name, gpu_memory in query(
                "eid", "uid", "creation", "username", "config.name", "config.gpu_memory"
            )
        ]
    )


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


def gpus(eid: str) -> Optional[int]:
    """
    Returns the configured device count an environment.
    """
    s = query("config.gpus", eid=eid)

    return int(s) if s else None


def gpu_memory(eid: str) -> Optional[str]:
    """
    Returns the configured amount of GPU memory of an environment.

    :param eid: Environment to query
    :return: The configured amount of GPU memory or None if not configured
    """
    return query("config.gpu_memory", eid=eid) or None


def activate(eid: str, uid: int, pid: int) -> None:
    """
    Activates an environment.
    """
    subprocess.check_output(
        f"genv exec envs activate --eid {eid} --uid {uid} --pid {pid}",
        shell=True,
    )


def configure(eid: str, command: str, value: Any) -> None:
    """
    Configures an environment.
    """
    ARGUMENTS = {
        "gpus": "--count",
        "gpu-memory": "--gpu-memory",
    }

    subprocess.check_output(
        f"genv exec envs config --eid {eid} {command} {ARGUMENTS[command]} {str(value)}",
        shell=True,
    )
