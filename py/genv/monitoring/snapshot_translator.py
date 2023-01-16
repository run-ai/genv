import json
import csv
from typing import Dict, IO

from genv import Snapshot, Device
from genv.monitoring.file_output_types import FileOutputType

host_csv_key = "host_name"


def snapshot_to_monitor_output(snapshots: Dict[str, Snapshot], fp: IO[str], output_type: FileOutputType = FileOutputType.CSV):
    if output_type == FileOutputType.CSV:
        monitor_output_csv(snapshots, fp)
    elif output_type == FileOutputType.JSON:
        monitor_output_json(snapshots, fp)


def monitor_output_csv(snapshots: Dict[str, Snapshot], fp: IO[str]):
    csv_keys = [host_csv_key, *Device.monitoring_data_keys()]

    writer = csv.DictWriter(fp, fieldnames=csv_keys, delimiter=',')
    writer.writeheader()

    for host_name, snapshot in snapshots.items():
        for device in snapshot.devices:
            row_dict = device.get_monitoring_data()
            row_dict[host_csv_key] = host_name
            writer.writerow(row_dict)


def monitor_output_json(snapshots: Dict[str, Snapshot], fp: IO[str]):
    devices = dict()
    for host_name, snapshot in snapshots.items():
        host_dict = dict()
        for device in snapshot.devices:
            host_dict[device.index] = device.get_monitoring_data()
        devices[host_name] = host_dict
    return json.dump(devices, fp=fp, indent=2)
