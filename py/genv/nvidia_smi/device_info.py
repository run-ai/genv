from dataclasses import dataclass


@dataclass
class DeviceInfo:
    uuid: str
    index: int
    utilization: int
    used_memory_bytes: str
    memory_utilization: int
