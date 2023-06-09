import argparse
import sys
from typing import Callable, Iterable, Optional

import genv

QUERIES = {
    "index": lambda device: device.index,
    "eids": lambda device: " ".join(device.eids),
    "total_memory": lambda device: device.total_memory,
    "attachments": lambda device: " ".join(
        f"{attachment.eid}+{attachment.gpu_memory or ''}+{attachment.time.replace(' ', '_')}"
        for attachment in device.attachments
    ),
}


def cleanup(
    snapshot: genv.Devices,
    eid: Optional[str] = None,
    count: Optional[int] = None,
) -> None:
    """
    Detaches devices from environments.

    :param snapshot:
    :param eid: If passed, detaches only from this environment. Otherwise, detaches all deactivated environments.
    :param count: Stops when this amount of devices are detached.
    :return: None
    """
    pred: Callable[[str], bool]

    if eid is not None:
        pred = lambda _: _ == eid
    else:
        envs = genv.core.envs.snapshot()
        pred = lambda eid: eid not in envs.eids

    for index in sorted(snapshot.indices, reverse=True):
        if count == 0:
            break

        device = snapshot[index]

        if device.detached:
            continue

        for candidate in device.eids:
            if not pred(candidate):
                continue

            device.detach(candidate)

        # TODO(raz): we have a bug here when an environment is attached to multiple devices
        # along with other environments.
        # we don't properly check if the detachment took place as we check if the device
        # is detached entirely.
        # therefore, 'count' is not respected and all devices are detached.

        if device.detached and count is not None:
            count -= 1


def do_attach(
    snapshot: genv.Devices,
    eid: str,
    count: Optional[int],
    index: Optional[int],
    allow_over_subscription: bool,
) -> None:
    """
    Attaches devices to an environment and prints the attached device indices.
    Either ensures that a specified count is attached to the environment
    or explicitly tries to attach a device with a given index.

    :param snapshot:
    :param eid: Environment identifier
    :param count: Amount of devices to attach
    :param index: Device index to attach
    :return: None
    """
    # TODO(raz): merge this method into genv.core.devices.attach() entirely

    envs = genv.core.envs.snapshot()

    if count is None and index is None:
        # use the environment device count configuration if set
        count = envs[eid].config.gpus if eid in envs else None

    gpu_memory = envs[eid].config.gpu_memory if eid in envs else None
    attached_devices = snapshot.filter(eid=eid)

    def ensure_count():
        """
        Attach or detach devices from the environment according to the number of devices
        set in the environment configuration.
        """
        current = len(attached_devices)

        if current < count:
            if count > len(snapshot):
                raise RuntimeError(
                    f"Requested more devices ({count}) than total available ({len(snapshot)})"
                )

            not_attached_devices = snapshot.filter(not_indices=attached_devices.indices)

            indices = not_attached_devices.find_available_devices(
                count - current, gpu_memory, allow_over_subscription
            )

            snapshot.attach(eid, indices, gpu_memory)
        elif current > count:
            cleanup(snapshot, eid, current - count)

    def attach_by_index():
        """
        Attach a specific device to the environment.
        """
        if index not in attached_devices.indices:
            if not allow_over_subscription and not snapshot[index].available(
                gpu_memory
            ):
                raise RuntimeError(f"Device {index} is not available")

            snapshot.attach(eid, index, gpu_memory)

    # TODO(raz): should this try/except be moved to main()?
    try:
        if count is not None:
            ensure_count()
        elif index is not None:
            attach_by_index()
    except RuntimeError as e:
        print(e, file=sys.stderr)
        exit(1)

    do_find(snapshot, eid)  # print the up-to-date device indices


def do_detach(
    snapshot: genv.Devices, eid: str, index: Optional[int], quiet: bool
) -> None:
    """
    Detaches devices from an environment. After detaching, print environment-devices current relationship.
    Either the device to detach is given, or a general cleanup is called on the environment.

    :param snapshot:
    :param eid: Environment identifier
    :param index: An index of the specific device to detach.
                If no index is given a general cleanup is called on the environment.
    :return: None
    """
    if index is not None:
        if index in snapshot.indices:
            snapshot[index].detach(eid)
    else:
        cleanup(snapshot, eid)

    if not quiet:
        do_find(snapshot, eid)  # print the up-to-date device indices


def do_find(snapshot: genv.Devices, eid: str) -> None:
    """
    Prints the indices of devices attached to the given environment.
    """

    print(",".join(str(index) for index in snapshot.filter(eid=eid).indices))


def do_ps(snapshot: genv.Devices, format: str, header: bool, timestamp: bool) -> None:
    """
    Prints information in a human-readable fashion to the standard output.

    :param snapshot:
    :param format: Which format should be used to print the devices data - "csv" or "tui".
    :param header: a flag instructing if we should print a header as part of the output.
    :param timestamp: a flag instructing if we should print attachment time as is or relative duration (now - creation).
    :return: None
    """
    if header:
        if format == "csv":
            print("ID,ENV ID,ENV NAME,ATTACHED")
        elif format == "tui":
            print("ID      ENV ID      ENV NAME        ATTACHED")

    def print_line(index, eid, name: Optional[str], attached):
        name = name or ""

        if format == "csv":
            print(f"{index},{eid},{name},{attached}")
        elif format == "tui":
            print(f"{index:<8}{eid:<12}{name:<16}{attached}")

    envs = genv.core.envs.snapshot()

    for device in snapshot:
        if device.detached:
            print_line(device.index, "", "", "")
        else:
            for attachment in device.attachments:
                index = device.index
                eid = attachment.eid
                name = envs[eid].config.name if eid in envs else None

                attached = (
                    attachment.time
                    if timestamp
                    else genv.utils.time_since(attachment.time)
                )

                print_line(index, eid, name, attached)


def do_query(snapshot: genv.Devices, queries: Iterable[str]) -> None:
    """
    Queries devices.
    """
    for device in snapshot:

        def query(name: str) -> str:
            result = QUERIES[name](device)

            return "" if result is None else str(result)

        print(",".join(query(name) for name in queries))


def add_arguments(parser: argparse.ArgumentParser) -> None:
    """
    Adds "genv devices" arguments to a parser.
    """

    parser.add_argument(
        "--no-cleanup",
        dest="cleanup",
        action="store_false",
        help="Do not perform clean up",
    )

    parser.add_argument("--reset", action="store_true", help="Reset previous state")

    subparsers = parser.add_subparsers(dest="command")

    def attach(parser):
        parser.add_argument("--eid", required=True, help="Environment identifier")
        parser.add_argument(
            "--allow-over-subscription",
            action="store_true",
            help="Use unavailable devices if needed",
        )
        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            # TODO(raz): remove this argument entirely.
            # either attach an environment to devices based on its configuration or by specific index
            "--count",
            type=int,
            help="Total devices count to be attached",
        )
        group.add_argument(
            "--index", type=int, help="Device index to attach specifically"
        )

    def detach(parser):
        parser.add_argument("--eid", required=True, help="Environment identifier")
        parser.add_argument("--index", type=int, help="Device index to dettach")
        parser.add_argument(
            "--quiet",
            action="store_true",
            help="Don't print updated device indexes",
        )

    def find(parser):
        parser.add_argument("--eid", required=True, help="Environment identifier")

    def ps(parser):
        parser.add_argument(
            "--no-header",
            dest="header",
            action="store_false",
            help="Do not print column headers",
        )
        parser.add_argument(
            "--timestamp", action="store_true", help="Print a non-prettified timestamp"
        )
        parser.add_argument(
            "--format",
            choices=["csv", "tui"],
            help="Output format; CSV or TUI (Text-based user interface)",
            default="tui",
        )

    def query(parser):
        parser.add_argument(
            "--query",
            "--queries",
            dest="queries",
            nargs="+",
            choices=QUERIES.keys(),
            required=True,
        )

    for command, help in [
        (attach, "Attach devices to an environment"),
        (detach, "Detach devices from an environment"),
        (find, "Find the devices attached to an enviornment"),
        (ps, "Print information about devices"),
        (query, "Query devices"),
    ]:
        command(subparsers.add_parser(command.__name__, help=help))


def run(args: argparse.Namespace) -> None:
    """
    Runs the "genv devices" logic.
    """

    with genv.utils.global_lock():
        with genv.core.devices.State(args.cleanup, args.reset) as devices:
            if args.command == "attach":
                do_attach(
                    devices,
                    args.eid,
                    args.count,
                    args.index,
                    args.allow_over_subscription,
                )
            elif args.command == "detach":
                do_detach(devices, args.eid, args.index, args.quiet)
            elif args.command == "find":
                do_find(devices, args.eid)
            elif args.command == "ps":
                do_ps(devices, args.format, args.header, args.timestamp)
            elif args.command == "query":
                do_query(devices, args.queries)
            else:
                do_ps(devices, format="tui", header=True, timestamp=False)
