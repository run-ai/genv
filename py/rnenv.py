import json
import os
from pathlib import Path

def env(name: str, default: str=None) -> str | None:
    return os.environ.get(f'RNENV_{name}', default)

def exists(filename: str) -> bool:
    return os.path.exists(path(filename))

def path(filename: str) -> str:
    return os.path.join(env('TMPDIR', '/var/tmp/rnenv'), filename)

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
