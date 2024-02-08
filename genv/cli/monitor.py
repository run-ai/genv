import argparse
import sys
import time

import genv


def add_arguments(parser: argparse.ArgumentParser) -> None:
    """
    Adds "genv monitor" arguments to a parser.
    """

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


async def run(args: argparse.Namespace) -> None:
    """
    Runs the "genv monitor" logic.
    """

    # NOTE(raz): we import depdendencies only here as they are optional
    try:
        from genv.metrics import Collection, publish_config_files, SPECS
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

    prometheus_client.start_http_server(args.port)

    publish_config_files(args.config_dir, prometheus_exporter_port=args.port)

    collection = Collection(SPECS)

    while True:
        system = await genv.core.system()

        with genv.utils.global_lock():
            snapshot = await genv.core.snapshot()

        collection.cleanup(system, snapshot)
        collection.update(system, snapshot)

        time.sleep(args.interval)
