from dataclasses import dataclass
from enum import Enum
from typing import Dict, List

class PipelineStage(Enum):
    FETCH = "fetch"
    DECODE = "decode"
    RENAME = "rename"
    DISPATCH = "dispatch"
    ISSUE = "issue"
    COMPLETE = "complete"
    RETIRE = "retire"


@dataclass
class Instruction:
    seq_num: int
    pc: str
    disasm: str
    opclass: str
    stages: Dict[PipelineStage, int]
    stage_order: List[PipelineStage]
