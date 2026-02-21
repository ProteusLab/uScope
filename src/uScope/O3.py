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

# NOTE: https://github.com/gem5/gem5/blob/stable/src/cpu/FuncUnit.py
class OpClass(Enum):
    IntAlu = "IntAlu"
    IntMult = "IntMult"
    IntDiv = "IntDiv"
    FloatAdd = "FloatAdd"
    FloatCmp = "FloatCmp"
    FloatCvt = "FloatCvt"
    Bf16Cvt = "Bf16Cvt"
    FloatMult = "FloatMult"
    FloatMultAcc = "FloatMultAcc"
    FloatMisc = "FloatMisc"
    FloatDiv = "FloatDiv"
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
    SimdExt = "SimdExt"
    SimdFloatExt = "SimdFloatExt"
    SimdConfig = "SimdConfig"
    SimdDotProd = "SimdDotProd"
    SimdAes = "SimdAes"
    SimdAesMix = "SimdAesMix"
    SimdSha1Hash = "SimdSha1Hash"
    SimdSha1Hash2 = "SimdSha1Hash2"
    SimdSha256Hash = "SimdSha256Hash"
    SimdSha256Hash2 = "SimdSha256Hash2"
    SimdShaSigma2 = "SimdShaSigma2"
    SimdShaSigma3 = "SimdShaSigma3"
    SimdSha3 = "SimdSha3"
    SimdSm4e = "SimdSm4e"
    SimdCrc = "SimdCrc"
    SimdBf16Add = "SimdBf16Add"
    SimdBf16Cmp = "SimdBf16Cmp"
    SimdBf16Cvt = "SimdBf16Cvt"
    SimdBf16DotProd = "SimdBf16DotProd"
    SimdBf16MatMultAcc = "SimdBf16MatMultAcc"
    SimdBf16Mult = "SimdBf16Mult"
    SimdBf16MultAcc = "SimdBf16MultAcc"
    SimdPredAlu = "SimdPredAlu"
    Matrix = "Matrix"
    MatrixMov = "MatrixMov"
    MatrixOP = "MatrixOP"
    System = "System"
    MemRead = "MemRead"
    FloatMemRead = "FloatMemRead"
    SimdUnitStrideLoad = "SimdUnitStrideLoad"
    SimdUnitStrideMaskLoad = "SimdUnitStrideMaskLoad"
    SimdUnitStrideSegmentedLoad = "SimdUnitStrideSegmentedLoad"
    SimdStridedLoad = "SimdStridedLoad"
    SimdIndexedLoad = "SimdIndexedLoad"
    SimdUnitStrideFaultOnlyFirstLoad = "SimdUnitStrideFaultOnlyFirstLoad"
    SimdUnitStrideSegmentedFaultOnlyFirstLoad = "SimdUnitStrideSegmentedFaultOnlyFirstLoad"
    SimdWholeRegisterLoad = "SimdWholeRegisterLoad"
    SimdStrideSegmentedLoad = "SimdStrideSegmentedLoad"
    MemWrite = "MemWrite"
    FloatMemWrite = "FloatMemWrite"
    SimdUnitStrideStore = "SimdUnitStrideStore"
    SimdUnitStrideMaskStore = "SimdUnitStrideMaskStore"
    SimdUnitStrideSegmentedStore = "SimdUnitStrideSegmentedStore"
    SimdStridedStore = "SimdStridedStore"
    SimdIndexedStore = "SimdIndexedStore"
    SimdWholeRegisterStore = "SimdWholeRegisterStore"
    SimdStrideSegmentedStore = "SimdStrideSegmentedStore"
    IprAccess = "IprAccess"
    InstPrefetch = "InstPrefetch"

    def __str__(self) -> str:
        return self.value
