import dataclasses
from typing import Iterable, Optional

from genv.entities import Snapshot, System
from genv.metrics import Collection as Base, Spec

from ..utils import Host


class Collection(Base):
    """
    A hostname aware metric collection.
    """

    def __init__(self, specs: Iterable[Spec]) -> None:
        return super().__init__(
            [
                dataclasses.replace(spec, labelnames=("hostname",) + spec.labelnames)
                for spec in specs
            ]
        )

    def cleanup(
        self,
        hosts: Iterable[Host],
        systems: Iterable[Optional[System]],
        snapshots: Iterable[Optional[Snapshot]],
    ) -> None:
        """
        Cleans up metric label values.
        """
        hostnames = [host.hostname for host in hosts]

        for metric in self:
            for labelvalues in metric.label_sets():
                if labelvalues[0] not in hostnames:
                    metric.remove(*labelvalues)

        for host, system, snapshot in zip(hosts, systems, snapshots):
            super().cleanup(system, snapshot, header=host.hostname)

    def update(
        self,
        hosts: Iterable[Host],
        systems: Iterable[Optional[System]],
        snapshots: Iterable[Optional[Snapshot]],
    ) -> None:
        """
        Updates metrics of hosts according to the given data.
        """
        for host, system, snapshot in zip(hosts, systems, snapshots):
            super().update(system, snapshot, labels={"hostname": host.hostname})
