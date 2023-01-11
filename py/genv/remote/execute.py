import json
from typing import Iterable

import genv.usage

from .utils import reprint
from .ssh import run_on_hosts


async def execute(
    hosts: Iterable[str],
    root: str,
    reports: Iterable[genv.usage.Report],
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

    stdouts = await run_on_hosts(
        hosts,
        root,
        "exec",
        "usage",
        "execute",
        stdins=[json.dumps(report, cls=genv.usage.JSONEncoder) for report in reports],
        sudo=True,
    )

    reprint(hosts, stdouts)
