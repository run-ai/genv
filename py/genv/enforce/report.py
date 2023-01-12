from dataclasses import dataclass
from typing import Iterable, Tuple

from ..envs import Env
from ..processes import Process


@dataclass
class Report:
    processes_to_terminate: Iterable[Process]
    envs_to_detach: Iterable[Tuple[Env, int]]

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

    def __bool__(self) -> bool:
        return bool(self.processes_to_terminate) or bool(self.envs_to_detach)
