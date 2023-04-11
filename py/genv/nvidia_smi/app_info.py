from dataclasses import dataclass


@dataclass
class AppInfo:
    pid: int
    gpu_uuid: str
    used_gpu_memory: str