from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Iterable, Optional, Union

from genv.utils import DATETIME_FMT

from .device import Device


@dataclass
class Devices:
    """
    A collection of devices.
    """

    devices: Iterable[Device]

    @property
    def indices(self) -> Iterable[int]:
        return [device.index for device in self.devices]

    def __iter__(self):
        return self.devices.__iter__()

    def __len__(self):
        return self.devices.__len__()

    def __getitem__(self, index: int) -> Device:
        return next(device for device in self.devices if device.index == index)

    def __contains__(self, index: int) -> bool:
        return index in self.indices

    def filter(
        self,
        deep: bool = True,
        *,
        indices: Optional[Iterable[int]] = None,
        not_indices: Optional[Iterable[int]] = None,
        eid: Optional[str] = None,
        eids: Optional[Iterable[str]] = None,
        attached: Optional[bool] = None,
        function: Optional[Callable[[Device], bool]] = None,
    ):
        """
        Returns a new filtered collection.

        :param deep: Perform deep filtering
        :param indices: Device indices to keep
        :param not_indices: Device indices to remove
        :param eid: Environment identifier to keep
        :param eids: Environment identifiers to keep
        :param attached: Keep only devices with environments attached or not
        :param function: Keep devices on which the lambda returns True
        """
        if eids:
            eids = set(eids)

        if eid:
            if not eids:
                eids = set()

            eids.add(eid)

        devices = self.devices

        if indices is not None:
            devices = [device for device in devices if device.index in indices]

        if not_indices is not None:
            devices = [device for device in devices if device.index not in not_indices]

        if eids is not None:
            if deep:
                devices = [device.filter(eids=eids) for device in devices]

            devices = [
                device
                for device in devices
                if any((eid in eids) for eid in device.eids)
            ]

        if attached is not None:
            if attached:
                devices = [device for device in devices if device.attached]
            else:
                devices = [device for device in devices if device.detached]

        if function is not None:
            devices = [device for device in devices if function(device)]

        return Devices(devices)

    def attach(
        self, eid: str, indices: Union[Iterable[int], int], gpu_memory: Optional[str]
    ) -> None:
        """
        Attaches devices to an environment.
        """

        if isinstance(indices, int):
            indices = [indices]

        time = datetime.now().strftime(DATETIME_FMT)

        for index in indices:
            self.devices[index].attach(eid, gpu_memory, time)
