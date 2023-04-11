from enum import Enum


class SnapshotMode(Enum):
    Full = 0
    Partial = 1  # information from nvidia-smi only
