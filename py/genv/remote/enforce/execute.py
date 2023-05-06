import json
from typing import Iterable

from genv.entities.enforce import Report

from genv.serialization import JSONEncoder

from ..utils import reprint, run, Config, Command


async def execute(config: Config, reports: Iterable[Report]) -> None:
    """
    Executes reports on multiple hosts.

    :param reports: Reports to execute on each host

    :return: None
    """
    command = Command(["exec", "usage", "execute"], sudo=True)

    hosts, stdouts = await run(
        config,
        command,
        stdins=[json.dumps(report, cls=JSONEncoder) for report in reports],
    )

    reprint([host.hostname for host in hosts], stdouts)
