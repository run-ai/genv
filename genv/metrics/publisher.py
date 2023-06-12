from dataclasses import dataclass
import os


class Base:
    def __init__(self, root: str, templates: str) -> None:
        self.root = root
        self.templates = templates

    def _path(self, *paths: str) -> str:
        return os.path.join(self.root, *paths)

    def copy_file(self, *paths: str, **kwargs: object) -> str:
        """
        Copy a file from the inputs directory to the output directory.
        The file contents are formatted with the passed keyword arguments.

        :return: Output file path
        """
        path = self._path(*paths)

        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(os.path.join(self.templates, *paths), "r") as f:
            contents = f.read()

        if kwargs:
            contents = contents.format(**kwargs)

        with open(path, "w") as f:
            f.write(contents)

        return path

    def publish(self) -> None:
        pass


class Prometheus(Base):
    @dataclass
    class Config:
        exporter_port: int

    def __init__(self, root: str, config: Config) -> None:
        self.config = config

        super().__init__(
            root, os.path.join(os.path.dirname(__file__), "export", "prometheus")
        )

    def publish(self) -> None:
        self.copy_file("prometheus.yml", exporter_port=self.config.exporter_port)


class Grafana(Base):
    @dataclass
    class Config:
        prometheus_url: str = "http://localhost:9090"

    def __init__(self, root: str, config: Config) -> None:
        self.config = config

        super().__init__(
            root, os.path.join(os.path.dirname(__file__), "export", "grafana")
        )

    def publish(self) -> None:
        overview_dashboard = self.copy_file("dashboards", "overview.json")

        self.copy_file(
            "provisioning",
            "datasources",
            "default.yml",
            prometheus_url=self.config.prometheus_url,
        )

        self.copy_file(
            "provisioning",
            "dashboards",
            "default.yml",
            dashboard_dir=self._path("dashboards"),
        )

        self.copy_file(
            "grafana.ini",
            provisioning=self._path("provisioning"),
            default_home_dashboard_path=overview_dashboard,
        )


def publish_config_files(root: str, *, prometheus_exporter_port: int) -> None:
    """
    Publish Prometheus and Grafana configuration files.
    """
    Prometheus(
        os.path.join(root, "prometheus"),
        Prometheus.Config(exporter_port=prometheus_exporter_port),
    ).publish()

    Grafana(
        os.path.join(root, "grafana"),
        Grafana.Config(),
    ).publish()
