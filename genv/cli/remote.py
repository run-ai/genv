import argparse
import asyncio
import dataclasses
import itertools
import os
import re
import shutil
import sys
from typing import Iterable, NoReturn, Optional, Tuple

import genv

QUERIES = {
    "hostname": lambda host, env: host.hostname,
    "eid": lambda host, env: env.eid,
    "creation": lambda host, env: env.creation,
}


async def find_available_host(
    config: genv.remote.Config, gpus: Optional[int]
) -> genv.remote.Host:
    """
    Finds a host with enough available resources.
    Raises 'RuntimeError' if cannot find such host.

    :param gpus: Device count specification

    :return: Host with enough available resources
    """
    # TODO(raz): avoid taking snapshots if not needed when 'gpus' is None
    hosts, snapshots = await genv.remote.core.devices.snapshot(config)

    for host, snapshot in zip(hosts, snapshots):
        if gpus is not None:
            available = len(snapshot.filter(attached=False))

            if available < gpus:
                continue

        return host

    raise RuntimeError("Cannot find a host with enough available resources")


def _exec_ssh(host: genv.remote.Host, command: str) -> NoReturn:
    """Replaces this process with an SSH connection.

    :param host: Remote host to connect to.
    :param command: Command to execute on the remote host.
    """

    path = shutil.which("ssh")

    # NOTE(raz): the '-t' argument is important as it makes the remote process to
    # terminate when the SSH connection gets disconnected (https://superuser.com/a/20708).
    args = [path, "-t", host.hostname, command]

    os.execv(path, args)


async def do_activate(
    config: genv.remote.Config,
    gpus: Optional[int],
    name: Optional[str],
    prompt: bool,
) -> NoReturn:
    """
    Finds a remote host with enough available resources, connects to it using SSH
    and activates an environment inside with the given specification.

    :param gpus: Device count specification
    :param name: Environment name specification
    :param prompt: Change the remote shell prompt

    :return: Does not return
    """
    host = await find_available_host(config, gpus)

    env = {"GENV_PREACTIVATE": 1, "GENV_PREACTIVATE_PROMPT": "1" if prompt else "0"}

    if gpus:
        env.update({"GENV_PREACTIVATE_GPUS": gpus})

    if name:
        env.update({"GENV_PREACTIVATE_ENVIRONMENT_NAME": name})

    path = shutil.which("ssh")
    args = (
        [path]
        + list(itertools.chain(*(["-o", f"SendEnv={variable}"] for variable in env)))
        + [host.hostname]
    )
    env = dict(os.environ, **{k: str(v) for k, v in env.items()})

    os.execve(path, args, env)


async def do_devices(
    config: genv.remote.Config,
    format: str,
    header: bool,
    summary: bool,
) -> None:
    """
    Prints information about devices on multiple hosts.

    :param format: Output format
    :param header: Print a header as part of the output
    :param summary: Print a summary as part of the output

    :return: None
    """
    hosts, snapshots = await genv.remote.core.devices.snapshot(config)

    if header:
        if format == "csv":
            print("HOST,TOTAL,AVAILABLE")
        elif format == "tui":
            print("HOST                     TOTAL    AVAILABLE")

    total = 0
    available = 0

    for host, snapshot in zip(hosts, snapshots):
        host_total = len(snapshot)
        host_available = len(snapshot.filter(attached=False))

        total += host_total
        available += host_available

        if format == "csv":
            print(f"{host.hostname},{host_total},{host_available}")
        elif format == "tui":
            print(f"{host.hostname:<25}{host_total:<9}{host_available}")

    if summary:
        print(
            f"\nTotal {total} devices with {available} available on {len(hosts)} hosts"
        )


async def do_enforce(
    config: genv.remote.Config,
    interval: int,
    non_env_processes: bool,
    env_devices: bool,
    env_memory: bool,
    max_devices_per_user: Optional[int],
    max_devices_for_user: Optional[Iterable[Tuple[str, int]]],
) -> None:
    """
    Enforce GPU usage on multiple hosts.

    :param interval: Interval in seconds; 0 means run once.

    :return: None
    """
    while True:
        hosts, snapshots = await genv.remote.core.snapshot(config)

        surveys = [
            genv.entities.enforce.Survey(snapshot, host.hostname)
            for host, snapshot in zip(hosts, snapshots)
        ]

        if non_env_processes:
            genv.enforce.rules.non_env_processes(*surveys)

        if env_devices:
            genv.enforce.rules.env_devices(*surveys)

        if env_memory:
            genv.enforce.rules.env_memory(*surveys)

        if max_devices_per_user is not None:
            genv.enforce.rules.max_devices_per_user(
                *surveys,
                maximum=max_devices_per_user,
                maximum_for_user=(
                    dict(max_devices_for_user) if max_devices_for_user else {}
                ),
            )

        reports = [survey.report for survey in surveys]

        await genv.remote.enforce.execute(
            config=genv.remote.Config(
                hosts=[host for host, report in zip(hosts, reports) if report],
                throw_on_error=config.throw_on_error,
                quiet=config.quiet,
            ),
            reports=[report for report in reports if report],
        )

        if interval == 0:
            break

        await asyncio.sleep(interval)


async def do_envs(
    config: genv.remote.Config,
    format: str,
    header: bool,
    summary: bool,
    timestamp: bool,
) -> None:
    """
    Prints information about active environments on multiple hosts.

    :param format: Output format
    :param header: Print a header as part of the output
    :param summary: Print a summary as part of the output

    :return: None
    """
    hosts, snapshots = await genv.remote.core.envs.snapshot(config)

    if header:
        if format == "csv":
            print("HOST,ID,USER,NAME,CREATED")
        elif format == "tui":
            print(
                "HOST                     ID      USER            NAME            CREATED"
            )

    for host, snapshot in zip(hosts, snapshots):
        for env in snapshot:
            user = env.username or ""
            name = env.config.name or ""
            created = env.creation if timestamp else env.time_since

            if format == "csv":
                print(f"{host.hostname},{env.eid},{user},{name},{created}")
            elif format == "tui":
                print(f"{host.hostname:<25}{env.eid:<8}{user:<16}{name:<16}{created}")

    if summary:
        print(
            f"\nTotal {sum([len(snapshot) for snapshot in snapshots])} environments on {len(hosts)} hosts"
        )


def _find_llm_port(env: genv.Env) -> Optional[int]:
    """Finds any port an LLM server environment listens on."""

    match = re.match(r"^llm/[^/]+/(\d+)$", env.config.name)
    if match:
        return int(match.group(1))


async def do_llm(config: genv.remote.Config, args: argparse.Namespace):
    """Runs the "genv llm" logic."""

    if args.llm_command == "attach":
        await do_llm_attach(config, args.model)
    elif args.llm_command == "ps":
        await do_llm_ps(config, args.format, args.header, args.summary, args.timestamp)
    elif args.llm_command == "serve":
        await do_llm_serve(config, args.model, args.gpus)
    else:
        await do_llm_ps(config)


async def do_llm_attach(config: genv.remote.Config, model: str) -> NoReturn:
    """
    Attaches to a running LLM on a remote host.
    Raises RuntimeError if could not find the LLM.

    :param model: Model name.
    """

    hosts, snapshots = await genv.remote.core.envs.snapshot(config)

    for host, snapshot in zip(hosts, snapshots):
        for env in snapshot:
            if not env.config.name:
                continue

            if not (
                env.config.name.startswith(f"llm/{model}/")
                or env.config.name == f"llm/{model}"  # before 1.4.1
            ):
                continue

            # TODO(raz): we currently attach to the first node; we should pick a node in a smarter way.
            _exec_ssh(host, f"genv llm attach {model}")

    raise RuntimeError(f"Could not find LLM model '{model}'")


async def do_llm_ps(
    config: genv.remote.Config,
    format: str = "tui",
    header: bool = True,
    summary: bool = True,
    timestamp: bool = False,
) -> None:
    """
    Prints information about active LLMs on remote hosts.

    :param format: Output format
    :param header: Print a header as part of the output
    :param summary: Print a summary as part of the output

    :return: None
    """
    hosts, snapshots = await genv.remote.core.envs.snapshot(config)

    if header:
        if format == "csv":
            print("HOST,MODEL,PORT,CREATED,EID,USER")
        elif format == "tui":
            print(
                "HOST                     MODEL       PORT    CREATED              EID     USER"
            )

    total = 0

    for host, snapshot in zip(hosts, snapshots):
        for env in snapshot:
            if not (env.config.name and env.config.name.startswith("llm/")):
                continue

            total += 1

            model = env.config.name.split("/")[1]
            port = _find_llm_port(env) or "N/A"
            created = env.creation if timestamp else env.time_since
            eid = env.eid
            user = env.username or ""

            if format == "csv":
                print(f"{host.hostname},{model},{port},{created},{eid}{user}")
            elif format == "tui":
                print(
                    f"{host.hostname:<25}{model:<12}{port:<8}{created:<21}{eid:<8}{user}"
                )

    if summary:
        print(f"\nTotal {total} LLMs on {len(hosts)} hosts")


async def do_llm_serve(
    config: genv.remote.Config,
    model: str,
    gpus: Optional[int],
) -> NoReturn:
    """Runs an LLM server in a newly created environment on a remote host."""

    host = await find_available_host(config, gpus)

    command = f"genv llm serve {model}"

    if gpus:
        command = f"{command} --gpus {gpus}"

    _exec_ssh(host, command)


async def do_monitor(
    config: genv.remote.Config, config_dir: str, port: int, interval: int
) -> None:
    """
    Runs a Prometheus exporter in the foreground and publishes Prometheus and Grafana config files.
    """
    try:
        from genv.metrics import publish_config_files, SPECS
        from genv.remote.metrics import Collection
        import prometheus_client
    except ModuleNotFoundError as e:
        if e.name != "prometheus_client":
            raise

        print(f"ERROR: Python package '{e.name}' is required", file=sys.stderr)
        exit(1)

    # https://github.com/prometheus/client_python#disabling-default-collector-metrics
    prometheus_client.REGISTRY.unregister(prometheus_client.GC_COLLECTOR)
    prometheus_client.REGISTRY.unregister(prometheus_client.PLATFORM_COLLECTOR)
    prometheus_client.REGISTRY.unregister(prometheus_client.PROCESS_COLLECTOR)

    prometheus_client.start_http_server(port)

    publish_config_files(config_dir, prometheus_exporter_port=port)

    collection = Collection(SPECS)

    while True:
        hosts, systems = await genv.remote.core.system(config)

        hosts_with_genv = [
            host for host, system in zip(hosts, systems) if system.genv.installed
        ]

        hosts_with_snapshots, snapshots = await genv.remote.core.snapshot(
            dataclasses.replace(config, hosts=hosts_with_genv)
        )

        hostname_to_snapshot = {
            host.hostname: snapshot
            for host, snapshot in zip(hosts_with_snapshots, snapshots)
        }

        # inflate snapshots to match hosts
        snapshots = [hostname_to_snapshot.get(host.hostname, None) for host in hosts]

        collection.cleanup(hosts, systems, snapshots)
        collection.update(hosts, systems, snapshots)

        await asyncio.sleep(interval)


async def do_query(
    config: genv.remote.Config, name: str, queries: Iterable[str]
) -> None:
    """
    Query environment data using a query string and print the results to the string.

    :param name: Environment name
    :param queries: List of query names

    :return: None
    """
    hosts, snapshots = await genv.remote.core.envs.snapshot(config)

    for host, snapshot in zip(hosts, snapshots):
        for env in snapshot:
            if env.config.name != name:
                continue

            def query(name: str) -> str:
                result = QUERIES[name](host, env)

                return "" if result is None else str(result)

            print(",".join(query(name) for name in queries))


def add_arguments(parser: argparse.ArgumentParser) -> None:
    """
    Adds "genv remote" arguments to a parser.
    """

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-H",
        "-host",
        "--host",
        dest="hostnames",
        help="Comma-separated hostnames or IP addresses",
    )
    group.add_argument(
        "-hostfile",
        "--hostfile",
        help="A file containing one hostname or IP address per line",
    )

    parser.add_argument(
        "-l",
        "--username",
        help="SSH login name",
    )

    parser.add_argument(
        "-t",
        "--timeout",
        type=int,
        help="SSH connection timeout",
    )

    parser.add_argument(
        "-e",
        "--exit-on-error",
        dest="throw_on_error",
        action="store_true",
        help="Exit on SSH error to one or more hosts (default: %(default)s)",
    )

    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Ignore SSH errors (default: %(default)s)",
    )

    subparsers = parser.add_subparsers(dest="command")

    def activate(parser):
        parser.add_argument("--name", help="Environment name")
        parser.add_argument("--gpus", type=int, help="Environment device count")
        parser.add_argument(
            "--no-prompt",
            dest="prompt",
            action="store_false",
            help="Don't change the shell prompt",
        )

    def devices(parser):
        parser.add_argument(
            "--no-header",
            dest="header",
            action="store_false",
            help="Do not print column headers",
        )
        parser.add_argument(
            "--no-summary",
            dest="summary",
            action="store_false",
            help="Do not print summary",
        )
        parser.add_argument(
            "--format",
            choices=["csv", "tui"],
            help="Output format; CSV or TUI (Text-based user interface)",
            default="tui",
        )

    def enforce(parser):
        parser.add_argument(
            "--interval",
            type=int,
            default=10,
            help="interval in seconds between enforcement cycles; 0 means run once (default: %(default)s)",
        )

        enforcements = parser.add_argument_group("enforcements")

        def add_enforcement(
            name: str, *, dest: str, help: str, default: bool = True
        ) -> None:
            """
            Adds a mutual exclusive group for an enforcement flag with true and false actions.
            """
            group = enforcements.add_mutually_exclusive_group()

            group.add_argument(
                f"--{name}",
                action="store_true",
                default=default,
                help=help + " (default: %(default)s)",
                dest=dest,
            )

            group.add_argument(
                f"--no-{name}",
                action="store_false",
                dest=dest,
            )

        add_enforcement(
            "non-env-processes",
            dest="non_env_processes",
            help="terminate processes that are not running in a GPU environment",
            default=False,
        )

        add_enforcement(
            "env-devices",
            dest="env_devices",
            help="enforce environment attached devices",
            default=True,
        )

        add_enforcement(
            "env-memory",
            dest="env_memory",
            help="enforce environment memory capacity if set",
            default=True,
        )

        enforcements.add_argument(
            "--max-devices-per-user",
            type=int,
            help="maximum allowed attached devices for each user",
        )

        def max_devices_for_user(value: str):
            try:
                username, maximum = value.split("=")

                return username, int(maximum)
            except (ValueError, SyntaxError):
                raise argparse.ArgumentTypeError(f"not a valid spec: {value}")

        enforcements.add_argument(
            "--max-devices-for-user",
            nargs="+",
            help="per-user specification of maximum allowed attached devices",
            metavar="username=maximum",
            type=max_devices_for_user,
        )

    def envs(parser):
        parser.add_argument(
            "--no-header",
            dest="header",
            action="store_false",
            help="Do not print column headers",
        )
        parser.add_argument(
            "--no-summary",
            dest="summary",
            action="store_false",
            help="Do not print summary",
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

    def llm(parser):
        subparsers = parser.add_subparsers(dest="llm_command")

        def attach(parser):
            parser.add_argument("model")

        def ps(parser):
            parser.add_argument(
                "--no-header",
                dest="header",
                action="store_false",
                help="Do not print column headers",
            )
            parser.add_argument(
                "--no-summary",
                dest="summary",
                action="store_false",
                help="Do not print summary",
            )
            parser.add_argument(
                "--timestamp",
                action="store_true",
                help="Print a non-prettified timestamp",
            )
            parser.add_argument(
                "--format",
                choices=["csv", "tui"],
                help="Output format; CSV or TUI (Text-based user interface)",
                default="tui",
            )

        def serve(parser):
            parser.add_argument("model")
            parser.add_argument("--gpus", type=int, help="Device count")

        for command, help in [
            (attach, "Attach to a running LLM model"),
            (ps, "Print information about active LLMs"),
            (serve, "Start an LLM server"),
        ]:
            command(subparsers.add_parser(command.__name__, help=help))

    def monitor(parser):
        parser.add_argument(
            "--config-dir",
            default=genv.utils.get_temp_file_path("metrics"),
            help="Directory to create Prometheus and Grafana config files at (default: %(default)s)",
        )

        parser.add_argument(
            "-p",
            "--port",
            type=int,
            default=8000,
            help="Port for Prometheus exporter to listen on (default: %(default)s)",
        )

        parser.add_argument(
            "-i",
            "--interval",
            type=int,
            default=10,
            help="Interval in seconds between collections (default: %(default)s)",
        )

    def query(parser):
        parser.add_argument("--name", required=True, help="Environment name")
        parser.add_argument(
            "--query",
            "--queries",
            dest="queries",
            nargs="+",
            choices=QUERIES.keys(),
            required=True,
        )

    for command, help in [
        (activate, "Activate environment in a remote host"),
        (devices, "Show device information from all hosts"),
        (enforce, "Enforce GPU usage on all hosts"),
        (envs, "List all active environments"),
        (llm, "Run and attach to LLMs on remote hosts"),
        (monitor, "Monitor remote hosts using Prometheus and Grafana"),
        (query, "Query environments or a specific one"),
    ]:
        submodule = command.__name__
        aliases = [f"{submodule}s"] if submodule in ["llm"] else []

        command(subparsers.add_parser(submodule, aliases=aliases, help=help))


def parse_hosts(args: argparse.Namespace) -> Iterable[genv.remote.Host]:
    """Parses arguments and returns a list of hosts."""

    if args.hostfile:
        with open(args.hostfile, "r") as f:
            hostnames = [
                line
                for line in [line.strip() for line in f.readlines()]
                if line and not line.startswith("#")
            ]
    else:
        hostnames = args.hostnames.split(",")

    def parse_host(hostname: str) -> genv.remote.Host:
        username, hostname = (
            hostname.split("@") if "@" in hostname else (args.username, hostname)
        )

        return genv.remote.Host(hostname, username, args.timeout)

    return [parse_host(hostname) for hostname in hostnames]


async def run(args: argparse.Namespace) -> None:
    """
    Runs the "genv remote" logic.
    """

    hosts = parse_hosts(args)
    config = genv.remote.Config(hosts, args.throw_on_error, args.quiet)

    if args.command == "activate":
        await do_activate(config, args.gpus, args.name, args.prompt)
    elif args.command == "devices":
        await do_devices(config, args.format, args.header, args.summary)
    elif args.command == "enforce":
        await do_enforce(
            config,
            args.interval,
            args.non_env_processes,
            args.env_devices,
            args.env_memory,
            args.max_devices_per_user,
            args.max_devices_for_user,
        )
    elif args.command == "envs":
        await do_envs(
            config,
            args.format,
            args.header,
            args.summary,
            args.timestamp,
        )
    elif args.command in ["llm", "llms"]:
        await do_llm(config, args)
    elif args.command == "monitor":
        await do_monitor(config, args.config_dir, args.port, args.interval)
    elif args.command == "query":
        await do_query(config, args.name, args.queries)
