import prometheus_client
from typing import Callable, Iterable, Optional, Tuple, TypeVar, Union

import genv

T = TypeVar("T", bound="Metric")


class Metric(prometheus_client.Gauge):
    def __init__(
        self,
        name: str,
        documentation: str,
        convert: Optional[Callable[[genv.Snapshot], float]] = None,
        labelnames: Tuple[str] = (),
        *args,
        **kwargs,
    ):
        super().__init__(name, documentation, labelnames, *args, **kwargs)
        self._kwargs["convert"] = self.convert = convert

    def labelvalues(self: T) -> Iterable[str]:
        with self._lock:
            return list(self._metrics.keys())

    def set(self, value: Union[float, genv.Snapshot]) -> None:
        """
        Sets the gague value.
        This could be explicit or using the provided conversion function on the given snapshot.
        Note that some metrics expect the snapshot to be already filtered.
        """
        if isinstance(value, genv.Snapshot):
            if self.convert is None:
                raise RuntimeError(
                    "Conversion function must be provided for metric when using snapshots"
                )

            value = self.convert(value)

        super().set(value)

    def cleanup(self, snapshot: genv.Snapshot) -> None:
        """
        Cleans up outdated metric labels.
        """
        pass


class System(Metric):
    pass


ENVIRONMENTS = System(
    "genv_environments_total",
    "Number of active environments",
    lambda snapshot: len(snapshot.envs),
)

PROCESSES = System(
    "genv_processes_total",
    "Number of running processes",
    lambda snapshot: len(snapshot.processes),
)

ATTACHED_DEVICES = System(
    "genv_attached_devices_total",
    "Number of attached devices",
    lambda snapshot: len(snapshot.devices.filter(attached=True)),
)

USERS = System(
    "genv_users_total",
    "Number of active users",
    lambda snapshot: len(snapshot.envs.usernames),
)

SYSTEM = [ENVIRONMENTS, PROCESSES, ATTACHED_DEVICES, USERS]


class Environment(Metric):
    def __init__(
        self,
        name: str,
        documentation: str,
        convert: Optional[Callable[[genv.Snapshot], float]] = None,
        labelnames: Tuple[str] = (),
        *args,
        **kwargs,
    ):
        super().__init__(
            name, documentation, convert, ("eid",) + labelnames, *args, **kwargs
        )

    def cleanup(self, snapshot: genv.Snapshot) -> None:
        for labels in self.labelvalues():
            eid = labels[0]

            if eid not in snapshot.envs.eids:
                self.remove(*labels)


ENVIRONMENT_PROCESSES = Environment(
    "genv_environment_processes_total",
    "Number of running processes in an environment",
    lambda snapshot: len(snapshot.processes),
)

ENVIRONMENT_ATTACHED_DEVICES = Environment(
    "genv_environment_attached_devices_total",
    "Number of attached devices of an environment",
    lambda snapshot: len(snapshot.devices),
)

ENVIRONMENT = [ENVIRONMENT_PROCESSES, ENVIRONMENT_ATTACHED_DEVICES]


class Process(Metric):
    def __init__(
        self,
        name: str,
        documentation: str,
        convert: Optional[Callable[[genv.Snapshot], float]] = None,
        labelnames: Tuple[str] = (),
        *args,
        **kwargs,
    ):
        super().__init__(
            name, documentation, convert, ("pid", "eid") + labelnames, *args, **kwargs
        )

    def cleanup(self, snapshot: genv.Snapshot) -> None:
        for labels in self.labelvalues():
            pid = int(labels[0])

            if pid not in snapshot.processes.pids:
                self.remove(*labels)


PROCESS_DEVICES = Process(
    "genv_process_devices_total",
    "Number of devices used by a process",
)

PROCESS_USED_GPU_MEMORY = Process(
    "genv_process_used_gpu_memory_bytes",
    "Used GPU memory by a process",
    labelnames=("device",),
)


PROCESS = [PROCESS_DEVICES, PROCESS_USED_GPU_MEMORY]


class User(Metric):
    def __init__(
        self,
        name: str,
        documentation: str,
        convert: Optional[Callable[[genv.Snapshot], float]] = None,
        labelnames: Tuple[str] = (),
        *args,
        **kwargs,
    ):
        super().__init__(
            name, documentation, convert, ("username",) + labelnames, *args, **kwargs
        )

    def cleanup(self, snapshot: genv.Snapshot) -> None:
        for labels in self.labelvalues():
            username = labels[0]

            if username not in snapshot.envs.usernames:
                self.remove(*labels)


USER_ENVIRONMENTS = User(
    "genv_user_environments_total",
    "Number of active environments of a user",
    lambda snapshot: len(snapshot.envs),
)

USER_PROCESSES = User(
    "genv_user_processes_total",
    "Number of running processes of a user",
    lambda snapshot: len(snapshot.processes),
)

USER_ATTACHED_DEVICES = User(
    "genv_user_attached_devices_total",
    "Number of attached devices of a user",
    lambda snapshot: len(snapshot.devices),
)

USER = [USER_ENVIRONMENTS, USER_PROCESSES, USER_ATTACHED_DEVICES]

ALL = SYSTEM + ENVIRONMENT + PROCESS + USER
