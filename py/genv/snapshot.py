from dataclasses import dataclass
from typing import Iterable

from . import processes as processes_
from . import envs as envs_
from . import devices as devices_


@dataclass
class Snapshot:
    processes: Iterable[processes_.Process]
    envs: Iterable[envs_.Env]
    devices: Iterable[devices_.Device]

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

    def attached(self) -> Iterable[devices_.Device]:
        """
        Returns devices with attached environments.
        """
        return [device for device in self.devices if len(device.eids) > 0]

    def filter(self, username: str):
        """
        Filters a snapshot by username.

        :return: A new snapshot with information related only to the given username.
        """
        envs = [env for env in self.envs if env.username == username]
        eids = [env.eid for env in envs]

        processes = [process for process in self.processes if process.eid in eids]

        devices = [
            devices_.Device(
                index=device.index,
                eids=[eid for eid in eids if eid in device.eids],
            )
            for device in self.devices
        ]

        return Snapshot(processes=processes, envs=envs, devices=devices)


# NOTE(raz): this method is not atomic because it runs manager executables in the background.
# each manager locks its state file and for this reason the snapshot is not coherent by definition.
# this should be done oppositely, by locking a single lock and querying all state files altogether.
async def snapshot() -> Snapshot:
    return Snapshot(
        processes=await processes_.snapshot(),
        envs=envs_.snapshot(),
        devices=devices_.snapshot(),
    )
