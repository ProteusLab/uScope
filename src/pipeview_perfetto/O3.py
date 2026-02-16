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


# NOTE https://github.com/gem5/gem5/blob/stable/src/cpu/o3/FuncUnitConfig.py
class OpClass(Enum):
    No_OpClass = "No_OpClass"
    IntAlu = "IntAlu"
    IntMult = "IntMult"
    IntDiv = "IntDiv"
    FloatAdd = "FloatAdd"
    FloatCmp = "FloatCmp"
    FloatCvt = "FloatCvt"
    FloatMult = "FloatMult"
    FloatMultAcc = "FloatMultAcc"
    FloatDiv = "FloatDiv"
    FloatMisc = "FloatMisc"
    FloatSqrt = "FloatSqrt"
    SimdAdd = "SimdAdd"
    SimdAddAcc = "SimdAddAcc"
    SimdAlu = "SimdAlu"
    SimdCmp = "SimdCmp"
    SimdCvt = "SimdCvt"
    SimdMisc = "SimdMisc"
    SimdMult = "SimdMult"
    SimdMultAcc = "SimdMultAcc"
    SimdMatMultAcc = "SimdMatMultAcc"
    SimdShift = "SimdShift"
    SimdShiftAcc = "SimdShiftAcc"
    SimdDiv = "SimdDiv"
    SimdSqrt = "SimdSqrt"
    SimdFloatAdd = "SimdFloatAdd"
    SimdFloatAlu = "SimdFloatAlu"
    SimdFloatCmp = "SimdFloatCmp"
    SimdFloatCvt = "SimdFloatCvt"
    SimdFloatDiv = "SimdFloatDiv"
    SimdFloatMisc = "SimdFloatMisc"
    SimdFloatMult = "SimdFloatMult"
    SimdFloatMultAcc = "SimdFloatMultAcc"
    SimdFloatMatMultAcc = "SimdFloatMatMultAcc"
    SimdFloatSqrt = "SimdFloatSqrt"
    SimdReduceAdd = "SimdReduceAdd"
    SimdReduceAlu = "SimdReduceAlu"
    SimdReduceCmp = "SimdReduceCmp"
    SimdFloatReduceAdd = "SimdFloatReduceAdd"
    SimdFloatReduceCmp = "SimdFloatReduceCmp"
    SimdAes = "SimdAes"
    SimdAesMix = "SimdAesMix"
    SimdSha1Hash = "SimdSha1Hash"
    SimdSha1Hash2 = "SimdSha1Hash2"
    SimdSha256Hash = "SimdSha256Hash"
    SimdSha256Hash2 = "SimdSha256Hash2"
    SimdShaSigma2 = "SimdShaSigma2"
    SimdShaSigma3 = "SimdShaSigma3"
    SimdPredAlu = "SimdPredAlu"
    Matrix = "Matrix"
    MatrixMov = "MatrixMov"
    MatrixOP = "MatrixOP"
    MemRead = "MemRead"
    MemWrite = "MemWrite"
    FloatMemRead = "FloatMemRead"
    FloatMemWrite = "FloatMemWrite"
    IprAccess = "IprAccess"
    InstPrefetch = "InstPrefetch"
    SimdUnitStrideLoad = "SimdUnitStrideLoad"
    SimdUnitStrideStore = "SimdUnitStrideStore"
    SimdUnitStrideMaskLoad = "SimdUnitStrideMaskLoad"
    SimdUnitStrideMaskStore = "SimdUnitStrideMaskStore"
    SimdStridedLoad = "SimdStridedLoad"
    SimdStridedStore = "SimdStridedStore"
    SimdIndexedLoad = "SimdIndexedLoad"
    SimdIndexedStore = "SimdIndexedStore"
    SimdWholeRegisterLoad = "SimdWholeRegisterLoad"
    SimdWholeRegisterStore = "SimdWholeRegisterStore"
    SimdUnitStrideFaultOnlyFirstLoad = "SimdUnitStrideFaultOnlyFirstLoad"
    SimdUnitStrideSegmentedLoad = "SimdUnitStrideSegmentedLoad"
    SimdUnitStrideSegmentedStore = "SimdUnitStrideSegmentedStore"
    SimdUnitStrideSegmentedFaultOnlyFirstLoad = "SimdUnitStrideSegmentedFaultOnlyFirstLoad"
    SimdStrideSegmentedLoad = "SimdStrideSegmentedLoad"
    SimdStrideSegmentedStore = "SimdStrideSegmentedStore"
    SimdExt = "SimdExt"
    SimdFloatExt = "SimdFloatExt"
    SimdConfig = "SimdConfig"

    def __str__(self):
        return self.value
