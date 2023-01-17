import asyncio
import json
from typing import Iterable

from ... import SshRunner, JSONEncoder
from ...enforce import Report
from ..utils import reprint


async def execute_report(
    hosts: Iterable[str],
    root: str,
    reports: Iterable[Report],
    cleanup: bool = True,
) -> None:
    """
    Executes reports on multiple hosts.

    :param hosts: list of Hostname or IP address
    :param root: Genv installation root directory
    :param reports: Reports to execute on each host
    :param cleanup: Don't execute empty reports
    """
    # TODO(raz): should this really be here?
    if cleanup:
        filtered = [(host, report) for host, report in zip(hosts, reports) if report]
        hosts = [_[0] for _ in filtered]
        reports = [_[1] for _ in filtered]

    genv_command = ["genv", "exec", "usage", "execute"]

    usage_commands = []
    for host_index in range(len(hosts)):
        host = hosts[host_index]
        report = reports[host_index]

        runner = SshRunner(host, process_env={"PATH": f'"{root}/bin:$PATH"'})
        command = runner.run_with_stdin(*genv_command, stdins=[json.dumps(report, cls=JSONEncoder)])
        usage_commands.append(command)
    stdouts = await asyncio.gather(*usage_commands)

    reprint(hosts, stdouts)
