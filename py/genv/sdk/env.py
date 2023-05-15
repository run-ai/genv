import os
from typing import Optional


def eid() -> Optional[str]:
    """
    Returns the current environment identifier or None if not running in one.
    """
    return os.environ.get("GENV_ENVIRONMENT_ID")


def active() -> bool:
    """
    Returns whether running in an active environment.
    """
    return eid() is not None
