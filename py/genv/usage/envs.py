from dataclasses import dataclass
from typing import Iterable, Optional

import genv.envs


@dataclass
class Env:
    eid: str
    username: Optional[str]
    name: Optional[str]

    def __hash__(self) -> int:
        return self.eid.__hash__()


def snapshot() -> Iterable[Env]:
    return [
        Env(eid, username or None, name or None)
        for eid, username, name in genv.envs.query("eid", "username", "config.name")
    ]
