import os


def get_prometheus_config_file_content(port: int) -> str:
    """
    Generates the contents of a Prometheus config file.
    """
    with open(
        os.path.join(os.path.dirname(__file__), "prometheus.yml.template"),
        "r",
    ) as f:
        template = f.read()

    return template.format(port=port)


def create_prometheus_config_file(port: int, path: str) -> None:
    """
    Creates a Prometheus configuration file.
    """
    contents = get_prometheus_config_file_content(port)

    with open(path, "w") as f:
        f.write(contents)
