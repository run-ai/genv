from datetime import datetime
import json
import os
from pathlib import Path
from typing import Optional

DATETIME_FMT = '%d/%m/%Y %H:%M:%S'

def env(name: str, default: str=None) -> Optional[str]:
    return os.environ.get(f'GENV_{name}', default)

def exists(filename: str) -> bool:
    return os.path.exists(path(filename))

def path(filename: str) -> str:
    return os.path.join(env('TMPDIR', '/var/tmp/genv'), filename)

def poll(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True

def read(filename: str) -> dict:
    with open(path(filename)) as f:
        return json.load(f)

def save(filename: str, o: dict) -> None:
    path_ = path(filename)
    Path(path_).parent.mkdir(parents=True, exist_ok=True)
    with open(path_, 'w') as f:
        json.dump(o, f)

def time_since(dt: datetime) -> str:
    value = int((datetime.now() - dt).total_seconds())
    unit = 'second'

    for amount, next in [
        (60, 'minute'),
        (60, 'hour'),
        (24, 'day'),
        (7, 'week'),
    ]:
        if value < amount:
            break

        value, _ = divmod(value, amount)
        unit = next

    if value > 1:
        unit = f'{unit}s'

    return f'{value} {unit} ago'
