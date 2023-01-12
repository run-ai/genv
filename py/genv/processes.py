import asyncio
from dataclasses import dataclass
import sys
from typing import Iterable, Optional

from . import nvidia_smi
from . import os_


@dataclass
class Process:
    """
    A compute running process either from an environment or not.
    """

    def __init__(self, *args_dict, **kwargs):
        """
        This ctor allows for deserializing of a partial representation of the object
            as well as the dataclass default usage. Either args_dict or kwargs expected.
        :param args_dict: Optional. A tuple containing a dict of the instance property names to values.
        :param kwargs: kwargs args for the object initialization.
        """
        if len(args_dict) == 1 and type(args_dict[0]) is dict:
            for arg_dict_item in args_dict[0].items():
                self.__dict__[arg_dict_item[0]] = arg_dict_item[1]
        elif kwargs:
            self.__dict__ = kwargs.copy()

        # Complete non-given items with the default of None
        property_names = self.__class__.__dict__['__dataclass_fields__'].keys()
        for property_name in property_names:
            if property_name not in self.__dict__:
                self.__dict__[property_name] = None

    @dataclass
    class Usage:
        """
        The GPU index and amount of GPU memory used by the process.
        """

        index: int
        gpu_memory: str

        def __init__(self, *args_dict, **kwargs):
            """
            This ctor allows for deserializing of a partial representation of the object
                as well as the dataclass default usage. Either args_dict or kwargs expected.
            :param args_dict: Optional. A tuple containing a dict of the instance property names to values.
            :param kwargs: kwargs args for the object initialization.
            """
            if len(args_dict) == 1 and type(args_dict[0]) is dict:
                for arg_dict_item in args_dict[0].items():
                    self.__dict__[arg_dict_item[0]] = arg_dict_item[1]
            elif kwargs:
                self.__dict__ = kwargs.copy()

            # Complete non-given items with the default of None
            property_names = self.__class__.__dict__['__dataclass_fields__'].keys()
            for property_name in property_names:
                if property_name not in self.__dict__:
                    self.__dict__[property_name] = None

    pid: int
    used_gpu_memory: Iterable[Usage]
    eid: Optional[str]

    def __hash__(self) -> int:
        return self.pid.__hash__()

    @staticmethod
    def eid(pid: int) -> Optional[str]:
        """
        Returns the environment identifier of the process with the given pid.
        Returns None if the process is not running in an environment or if it could not be queried.
        """
        try:
            return os_.get_process_environ(pid).get("GENV_ENVIRONMENT_ID")
        except PermissionError:
            print(
                f"[WARNING] Not enough permissions to query environment of process {pid}",
                file=sys.stderr,
            )
        except FileNotFoundError:
            print(f"[DEBUG] Process {pid} already terminated", file=sys.stderr)


async def snapshot() -> Iterable[Process]:
    """
    Returns a snapshot of all running compute processes.
    """
    uuids, apps = await asyncio.gather(
        nvidia_smi.device_uuids(), nvidia_smi.compute_apps()
    )

    pid_to_apps = {
        pid: [app for app in apps if app["pid"] == pid]
        for pid in set(app["pid"] for app in apps)
    }

    return [
        Process(
            pid=pid,
            used_gpu_memory=[
                Process.Usage(
                    index=uuids[app["gpu_uuid"]], gpu_memory=app["used_gpu_memory"]
                )
                for app in apps
            ],
            eid=Process.eid(pid),
        )
        for pid, apps in pid_to_apps.items()
    ]
