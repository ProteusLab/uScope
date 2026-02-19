from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional

@dataclass
class Event:
    name: str
    pid: int

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return {k: v for k, v in d.items() if v is not None}


@dataclass
class MetadataEvent(Event):
    args: Dict[str, Any]
    ph: str = "M"
    tid: Optional[int] = None


@dataclass
class DurationEvent(Event):
    ts: int
    dur: int
    cat: str
    args: Dict[str, Any]
    cname: Optional[str] = None
    ph: str = "X"
    tid: Optional[int] = None
