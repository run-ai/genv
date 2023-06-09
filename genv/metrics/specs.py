import inspect
import sys

from .spec import Spec, Type


def Device(*args, **kwargs) -> Spec:
    """
    Returns a per-device metric specification.
    """
    labelnames = kwargs.pop("labelnames", tuple())

    return Spec(
        Type.Device,
        *args,
        **kwargs,
        labelnames=("index",) + labelnames,
    )


DEVICE_UTILIZATION = Device(
    "genv_device_utilization",
    "Device utilization",
)

DEVICE_MEMORY_USED = Device(
    "genv_device_memory_used_bytes",
    "Device used memory in bytes",
)


def System(*args, **kwargs) -> Spec:
    """
    Returns a system-wide metric specification.
    """
    return Spec(Type.System, *args, **kwargs)


ENVIRONMENTS = System(
    "genv_environments_total",
    "Number of active environments",
    convert=lambda snapshot: len(snapshot.envs),
)

PROCESSES = System(
    "genv_processes_total",
    "Number of running processes",
    convert=lambda snapshot: len(snapshot.processes),
)

ATTACHED_DEVICES = System(
    "genv_attached_devices_total",
    "Number of attached devices",
    convert=lambda snapshot: len(snapshot.devices.filter(attached=True)),
)

USERS = System(
    "genv_users_total",
    "Number of active users",
    convert=lambda snapshot: len(snapshot.envs.usernames),
)


def Environment(*args, **kwargs) -> Spec:
    """
    Returns a per-environment metric specification.
    """
    labelnames = kwargs.pop("labelnames", tuple())

    return Spec(
        Type.Environment,
        *args,
        **kwargs,
        labelnames=("eid",) + labelnames,
        filter=lambda labels, snapshot: labels[0] in snapshot.envs.eids,
    )


ENVIRONMENT_PROCESSES = Environment(
    "genv_environment_processes_total",
    "Number of running processes in an environment",
    convert=lambda snapshot: len(snapshot.processes),
)

ENVIRONMENT_ATTACHED_DEVICES = Environment(
    "genv_environment_attached_devices_total",
    "Number of attached devices of an environment",
    convert=lambda snapshot: len(snapshot.devices),
)


def Process(*args, **kwargs) -> Spec:
    """
    Returns a per-process metric specification.
    """
    labelnames = kwargs.pop("labelnames", tuple())

    return Spec(
        Type.Process,
        *args,
        **kwargs,
        labelnames=("pid", "eid") + labelnames,
        filter=lambda labels, snapshot: int(labels[0]) in snapshot.processes.pids,
    )


PROCESS_DEVICES = Process(
    "genv_process_devices_total",
    "Number of devices used by a process",
)

PROCESS_USED_GPU_MEMORY = Process(
    "genv_process_used_gpu_memory_bytes",
    "Used GPU memory by a process",
    labelnames=("device",),
)


def User(*args, **kwargs) -> Spec:
    """
    Returns a per-user metric specification.
    """
    labelnames = kwargs.pop("labelnames", tuple())

    return Spec(
        Type.User,
        *args,
        **kwargs,
        labelnames=("username",) + labelnames,
        filter=lambda labels, snapshot: labels[0] in snapshot.envs.usernames,
    )


USER_ENVIRONMENTS = User(
    "genv_user_environments_total",
    "Number of active environments of a user",
    convert=lambda snapshot: len(snapshot.envs),
)

USER_PROCESSES = User(
    "genv_user_processes_total",
    "Number of running processes of a user",
    convert=lambda snapshot: len(snapshot.processes),
)

USER_ATTACHED_DEVICES = User(
    "genv_user_attached_devices_total",
    "Number of attached devices of a user",
    convert=lambda snapshot: len(snapshot.devices),
)


ALL = [
    spec
    for _, spec in inspect.getmembers(
        sys.modules[__name__], lambda o: isinstance(o, Spec)
    )
]
