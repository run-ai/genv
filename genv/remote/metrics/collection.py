from typing import Iterable

from genv.entities import Snapshot
from genv.metrics import Collection as Base, Spec

from ..utils import Host


class Collection(Base):
    """
    A hostname aware metric collection.
    """

    def __init__(self, specs: Iterable[Spec]) -> None:
        return super().__init__(
            [
                Spec(
                    spec.type,
                    spec.name,
                    spec.documentation,
                    ("hostname",) + spec.labelnames,
                    spec.convert,
                    spec.filter,
                )
                for spec in specs
            ]
        )

    def cleanup(self, hosts: Iterable[Host], snapshots: Iterable[Snapshot]) -> None:
        """
        Cleans up metric label values.
        """
        hostname_to_snapshot = {
            host.hostname: snapshot for host, snapshot in zip(hosts, snapshots)
        }

        for metric in self:

            def filter(label_set: Iterable[str]) -> bool:
                hostname, *label_set = label_set

                if hostname not in hostname_to_snapshot:
                    return False

                if metric.filter and not metric.filter(
                    label_set, hostname_to_snapshot[hostname]
                ):
                    return False

                return True

            metric.cleanup(filter)

    def update(self, hosts: Iterable[Host], snapshots: Iterable[Snapshot]) -> None:
        """
        Updates metrics of hosts according to the given snapshots.
        """
        for host, snapshot in zip(hosts, snapshots):
            super().update(snapshot, labels={"hostname": host.hostname})
