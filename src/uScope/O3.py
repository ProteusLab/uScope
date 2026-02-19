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

    @staticmethod
    def order():
        return [ PipelineStage.FETCH,
                 PipelineStage.DECODE,
                 PipelineStage.RENAME,
                 PipelineStage.DISPATCH,
                 PipelineStage.ISSUE,
                 PipelineStage.COMPLETE,
                 PipelineStage.RETIRE ]

    def __str__(self) -> str:
        return self.value

@dataclass
class Instruction:
    UNKNOWN = "UNKNOWN"

    seq_num: int
    pc: str
    disasm: str
    opclass: str
    stages: Dict[PipelineStage, int]
    stage_order: List[PipelineStage]

    @property
    def mnemonic(self):
        if not self.disasm:
            return Instruction.UNKNOWN
        return self.disasm.split()[0].upper()
