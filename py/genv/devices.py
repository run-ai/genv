from dataclasses import dataclass
import subprocess
from typing import Dict, Iterable, Optional


# NOTE(raz): This should be the layer that queries and controls the state of Genv regarding devices.
# Currently, it relies on executing the device manager executable of Genv, as this is where the logic is implemented.
# This however should be done oppositely.
# The entire logic that queries and controls devices.json should be implemented here, and the device manager executable
# should use methods from here.
# It should take the Genv lock for the atomicity of the transaction, and print output as needed.
# The current architecture has an inherent potential deadlock because each manager locks a different lock, and might
# call the other manager.



@dataclass
class Device:
    index: int
    eids: Iterable[str]
    memory: Optional[int]

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


def snapshot() -> Iterable[Device]:
    return [Device(index, d["eids"]) for index, d in ps().items()]


def ps() -> Dict[int, Iterable[str]]:
    """
    Returns information about device and active attachments.

    :return: A mapping between device index and all attached environment identifiers
    """
    devices = dict()

    for line in (
        subprocess.check_output(
            "genv exec devices ps --no-header --format csv", shell=True
        )
        .decode("utf-8")
        .strip()
        .splitlines()
    ):
        index, eid, _, _ = line.split(",")
        index = int(index)

        if index not in devices:
            devices[index] = {"eids": []}

        if eid:
            devices[index]["eids"].append(eid)

    return devices


def detach(eid: str, index: int) -> None:
    """
    Detaches an environment from a device.

    :param eid: Environment identifier
    :param index: Device index
    :return: None
    """
    # TODO(raz): support detaching from multiple devices at the same time
    subprocess.check_call(
        f"genv exec devices detach --quiet --eid {eid} --index {index}", shell=True
    )
