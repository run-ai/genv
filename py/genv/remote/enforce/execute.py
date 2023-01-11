import json
from typing import Iterable

from ...json_ import JSONEncoder
from ...enforce import Report

from ..utils import reprint
from ..ssh import run


async def execute(
    hosts: Iterable[str],
    root: str,
    reports: Iterable[Report],
    cleanup: bool = True,
) -> None:
    """
    Executes reports on multiple hosts.

    :param host: Hostname or IP address
    :param root: Genv installation root directory
    :param reports: Reports to execute on each host
    :param cleanup: Don't execute empty reports
    """
    # TODO(raz): should this really be here?
    if cleanup:
        filtered = [(host, report) for host, report in zip(hosts, reports) if report]
        hosts = [_[0] for _ in filtered]
        reports = [_[1] for _ in filtered]

    stdouts = await run(
        hosts,
        root,
        "exec",
        "usage",
        "execute",
        stdins=[json.dumps(report, cls=JSONEncoder) for report in reports],
        sudo=True,
    )

    reprint(hosts, stdouts)
