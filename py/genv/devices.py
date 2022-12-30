from collections import defaultdict
import subprocess
from typing import Dict, Iterable


# NOTE(raz): This should be the layer that queries and controls the state of Genv regarding devices.
# Currently, it relies on executing the device manager executable of Genv, as this is where the logic is implemented.
# This however should be done oppositely.
# The entire logic that queries and controls devices.json should be implemented here, and the device manager executable
# should use methods from here.
# It should take the Genv lock for the atomicity of the transaction, and print output as needed.
# The current architecture has an inherent potential deadlock because each manager locks a different lock, and might
# call the other manager.


def attachments() -> Dict[int, Iterable[str]]:
    """
    Returns all active device attachments.

    :return: A mapping between device index and all attached environment identifiers
    """
    attachments = defaultdict(list)

    for line in (
        subprocess.check_output(
            "genv exec devices ps --no-header --format csv", shell=True
        )
        .decode("utf-8")
        .strip()
        .splitlines()
    ):
        index, eid, _, _ = line.split(",")

        if eid:
            attachments[int(index)].append(eid)

    return dict(attachments)


def detach(eid: str, index: int) -> None:
    """
    Detaches an environment from a device.

    :param eid: Environment identifier
    :param index: Device index
    :return: None
    """
    # TODO(raz): support detaching from multiple devices at the same time
    subprocess.check_call(
        f"genv exec devices detach --quiet --eid {eid} --index {index}", shell=True
    )
