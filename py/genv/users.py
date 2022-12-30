from typing import Dict, Iterable

from . import devices
from . import envs


def attachments() -> Dict[str, Dict[int, Iterable[str]]]:
    """
    Returns active device attachments of users.
    """
    usernames = envs.usernames()

    attachments = dict()

    for index, eids in devices.attachments().items():
        for eid in eids:
            username = usernames.get(eid)

            if username not in attachments:
                attachments[username] = dict()

            if index not in attachments[username]:
                attachments[username][index] = list()

            attachments[username][index].append(eid)

    return attachments
