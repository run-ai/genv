import prometheus_client

# system

ENVIRONMENTS = prometheus_client.Gauge(
    "genv_environments_total",
    "Number of active environments",
)

PROCESSES = prometheus_client.Gauge(
    "genv_processes_total",
    "Number of running processes",
)

ATTACHED_DEVICES = prometheus_client.Gauge(
    "genv_attached_devices_total",
    "Number of attached devices",
)

USERS = prometheus_client.Gauge(
    "genv_users_total",
    "Number of active users",
)

# per environment

DEFAULT_ENVIRONMENT_LABELS = ["eid"]

ENVIRONMENT_PROCESSES = prometheus_client.Gauge(
    "genv_environment_processes_total",
    "Number of running processes in an environment",
    DEFAULT_ENVIRONMENT_LABELS,
)

ENVIRONMENT_ATTACHED_DEVICES = prometheus_client.Gauge(
    "genv_environment_attached_devices_total",
    "Number of attached devices of an environment",
    DEFAULT_ENVIRONMENT_LABELS,
)

# per process

DEFAULT_PROCESS_LABELS = ["pid", "eid"]

PROCESS_DEVICES = prometheus_client.Gauge(
    "genv_process_devices_total",
    "Number of devices used by a process",
    DEFAULT_PROCESS_LABELS,
)

PROCESS_USED_GPU_MEMORY = prometheus_client.Gauge(
    "genv_process_used_gpu_memory_bytes",
    "Used GPU memory by a process",
    DEFAULT_PROCESS_LABELS + ["device"],
)

# per user

DEFAULT_USER_LABELS = ["username"]

USER_ENVIRONMENTS = prometheus_client.Gauge(
    "genv_user_environments_total",
    "Number of active environments of a user",
    DEFAULT_USER_LABELS,
)

USER_PROCESSES = prometheus_client.Gauge(
    "genv_user_processes_total",
    "Number of running processes of a user",
    DEFAULT_USER_LABELS,
)

USER_ATTACHED_DEVICES = prometheus_client.Gauge(
    "genv_user_attached_devices_total",
    "Number of attached devices of a user",
    DEFAULT_USER_LABELS,
)
