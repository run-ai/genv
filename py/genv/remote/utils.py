import sys
from typing import Iterable, TextIO


def reprint(
    hosts: Iterable[str], outputs: Iterable[str], file: TextIO = sys.stdout
) -> None:
    """
    Reprints outputs from multiple hosts with the hostname as a prefix.

    :param hosts: Hostnames or IP addresses
    :param outputs: Output for every host
    :param file: Output to print to
    """
    for host, output in zip(hosts, outputs):
        for line in output.splitlines():
            print(f"[{host}] {line}", file=file)
