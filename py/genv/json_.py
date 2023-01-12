import json
from typing import Any, Dict

from .devices import Device
from .envs import Env
from .processes import Process
from .snapshot import Snapshot
from .enforce import Report

Types = [Device, Env, Process, Process.Usage, Report, Snapshot]


class JSONEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Dict:
        if o.__class__ in Types:
            return o.__dict__

        return super().default(o)


class JSONDecoder(json.JSONDecoder):
    def __init__(self) -> None:
        super().__init__(object_hook=self.object_hook)

    def object_hook(self, d: Dict) -> Any:
        # all classes are Python dataclasses and therefore have a constructor that receive all members as arguments.
        # we rely on `co_varnames` to find them dynamically.
        # here's the documentation: https://docs.python.org/3.7/reference/datamodel.html#index-55.
        for cls in Types:
            class_properties = set(cls.__dict__['__dataclass_fields__'].keys())

            if set(d.keys()).issubset(class_properties):
                return cls(d)

        return d
