# tests/test_parser.py
import pytest

from uScope.parser import PipeViewParser
from uScope.O3 import PipelineStage, Instruction


def assert_instruction(instr: Instruction, seq_num : int, pc : str, disasm : str, opclass : str, expected_stages, stage_order):

    assert isinstance(instr, Instruction)

    if seq_num is not None:
        assert instr.seq_num == seq_num
    if pc is not None:
        assert instr.pc == pc
    if disasm is not None:
        assert instr.disasm == disasm
    if opclass is not None:
        assert instr.opclass == opclass
    if stage_order is not None:
        assert instr.stage_order == stage_order
    if expected_stages:
        for stage, expected in expected_stages.items():
            if expected is None:
                assert stage not in instr.stages
            else:
                assert stage in instr.stages, f"Stage {stage} missing"
                assert instr.stages[stage] == expected, f"Stage {stage} value mismatch"


def assert_instructions(parser, expected, stage_order):
    assert len(parser.instructions) == len(expected)
    for seq_num, (pc, disasm, opclass, stages) in expected.items():
        assert_instruction(
            instr=parser.instructions[seq_num],
            seq_num=seq_num,
            pc=pc,
            disasm=disasm,
            opclass=opclass,
            stage_order=stage_order,
            expected_stages=stages
        )


def test_parse_in_order(trace_with_in_order):
    parser = PipeViewParser()
    parser.parse_file(str(trace_with_in_order))

    all_stages = PipelineStage.order()
    expected = {
        1: ("0x1000", "add x1, x2, x3", "IntAlu", {
            PipelineStage.FETCH: 1000, PipelineStage.DECODE: 1100,
            PipelineStage.RENAME: 1150, PipelineStage.DISPATCH: 1200,
            PipelineStage.ISSUE: 1300, PipelineStage.COMPLETE: 1400,
            PipelineStage.RETIRE: 1500
        }),
        2: ("0x1004", "lw a0, 0(a1)", "MemRead", {
            PipelineStage.FETCH: 2000, PipelineStage.DECODE: 2100,
            PipelineStage.RENAME: 2150, PipelineStage.DISPATCH: 2200,
            PipelineStage.ISSUE: 2300, PipelineStage.COMPLETE: 2400,
            PipelineStage.RETIRE: 2500
        }),
        3: ("0x1008", "mul x10, x21, x11", "IntMult", {
            PipelineStage.FETCH: 3000, PipelineStage.DECODE: 0,
            PipelineStage.RENAME: 0, PipelineStage.DISPATCH: 0,
            PipelineStage.ISSUE: 0, PipelineStage.COMPLETE: 0,
            PipelineStage.RETIRE: 0
        }),
    }
    assert_instructions(parser, expected, all_stages)


def test_parse_squashed(trace_with_squashed):
    parser = PipeViewParser()
    parser.parse_file(str(trace_with_squashed))

    all_stages = PipelineStage.order()
    expected = {
        1: ("0x1000", "lw a1, 4(a1)", "MemRead", {
            PipelineStage.FETCH: 1000,
            PipelineStage.DECODE: 0, PipelineStage.RENAME: 0,
            PipelineStage.DISPATCH: 0, PipelineStage.ISSUE: 0,
            PipelineStage.COMPLETE: 0, PipelineStage.RETIRE: 0
        }),
        2: ("0x1004", "lw a0, 0(a1)", "MemRead", {
            PipelineStage.FETCH: 2000,
            PipelineStage.DECODE: 0, PipelineStage.RENAME: 0,
            PipelineStage.DISPATCH: 0, PipelineStage.ISSUE: 0,
            PipelineStage.COMPLETE: 0, PipelineStage.RETIRE: 0
        }),
    }
    assert_instructions(parser, expected, all_stages)


def test_parse_missing_stages(trace_with_missing_stages):
    parser = PipeViewParser()
    parser.parse_file(str(trace_with_missing_stages))

    expected_order = [
        PipelineStage.FETCH,
        PipelineStage.DECODE,
        PipelineStage.RENAME,
        PipelineStage.ISSUE,
        PipelineStage.COMPLETE,
        PipelineStage.RETIRE,
    ]
    expected = {
        1: (None, None, None, {
            PipelineStage.FETCH: 1000,
            PipelineStage.DECODE: 1100,
            PipelineStage.RENAME: 1150,
            PipelineStage.ISSUE: 1300,
            PipelineStage.COMPLETE: 1400,
            PipelineStage.RETIRE: 1500,
        }),
    }
    assert_instructions(parser, expected, expected_order)
    assert PipelineStage.DISPATCH not in parser.instructions[1].stages


def test_parse_empty_lines(trace_with_empty_lines):
    parser = PipeViewParser()
    parser.parse_file(str(trace_with_empty_lines))

    all_stages = PipelineStage.order()
    expected = {
        1: ("0x1000", "add x1, x2, x3", "IntAlu", {
            PipelineStage.FETCH: 1000, PipelineStage.DECODE: 1100,
            PipelineStage.RENAME: 1150, PipelineStage.DISPATCH: 1200,
            PipelineStage.ISSUE: 1300, PipelineStage.COMPLETE: 1400,
            PipelineStage.RETIRE: 1500
        }),
        2: ("0x2000", "lw a0, 0(a1)", "MemRead", {
            PipelineStage.FETCH: 2000, PipelineStage.DECODE: 2100,
            PipelineStage.RENAME: 2150, PipelineStage.DISPATCH: 2200,
            PipelineStage.ISSUE: 2300, PipelineStage.COMPLETE: 2400,
            PipelineStage.RETIRE: 2500
        }),
    }
    assert_instructions(parser, expected, all_stages)


def test_parse_invalid_lines(trace_with_invalid_lines):
    parser = PipeViewParser()
    parser.parse_file(str(trace_with_invalid_lines))

    all_stages = PipelineStage.order()
    expected = {
        1: ("0x1000", "add x1, x2, x3", "IntAlu", {
            PipelineStage.FETCH: 1000, PipelineStage.DECODE: 1100,
            PipelineStage.RENAME: 1150, PipelineStage.DISPATCH: 1200,
            PipelineStage.ISSUE: 1300, PipelineStage.COMPLETE: 1400,
            PipelineStage.RETIRE: 1500,
        }),
    }
    assert_instructions(parser, expected, all_stages)


def test_parse_ilp(trace_with_ilp):
    parser = PipeViewParser()
    parser.parse_file(str(trace_with_ilp))

    all_stages = PipelineStage.order()
    expected = {
        1: ("0x1000", "add x3, x1, x2", "IntAlu", {
            PipelineStage.FETCH: 1000, PipelineStage.DECODE: 1100,
            PipelineStage.RENAME: 1150, PipelineStage.DISPATCH: 1200,
            PipelineStage.ISSUE: 1300, PipelineStage.COMPLETE: 1400,
            PipelineStage.RETIRE: 1500
        }),
        2: ("0x1004", "add x3, x2, x4", "IntAlu", {
            PipelineStage.FETCH: 1000, PipelineStage.DECODE: 1100,
            PipelineStage.RENAME: 1150, PipelineStage.DISPATCH: 1200,
            PipelineStage.ISSUE: 1300, PipelineStage.COMPLETE: 1400,
            PipelineStage.RETIRE: 1500
        }),
    }
    assert_instructions(parser, expected, all_stages)


def test_parse_pipelined(trace_with_pipelined):
    parser = PipeViewParser()
    parser.parse_file(str(trace_with_pipelined))

    all_stages = PipelineStage.order()
    expected = {
        53: ("0x000101b4", "div a7, a4, a5", "IntDiv", {
            PipelineStage.FETCH: 137000, PipelineStage.DECODE: 137500,
            PipelineStage.RENAME: 138000, PipelineStage.DISPATCH: 139000,
            PipelineStage.ISSUE: 192500, PipelineStage.COMPLETE: 202500,
            PipelineStage.RETIRE: 203500
        }),
        54: ("0x000101b8", "add s2, a6, a7", "IntAlu", {
            PipelineStage.FETCH: 137000, PipelineStage.DECODE: 137500,
            PipelineStage.RENAME: 138000, PipelineStage.DISPATCH: 139000,
            PipelineStage.ISSUE: 202500, PipelineStage.COMPLETE: 203000,
            PipelineStage.RETIRE: 204000
        }),
        55: ("0x000101bc", "sw s2, 0(a2)", "MemWrite", {
            PipelineStage.FETCH: 137000, PipelineStage.DECODE: 137500,
            PipelineStage.RENAME: 138000, PipelineStage.DISPATCH: 139000,
            PipelineStage.ISSUE: 203000, PipelineStage.COMPLETE: 203500,
            PipelineStage.RETIRE: 204500
        }),
    }
    assert_instructions(parser, expected, all_stages)


def test_parse_unordered(trace_with_unordered):
    parser = PipeViewParser()
    parser.parse_file(str(trace_with_unordered))

    all_stages = PipelineStage.order()
    expected = {
        2: ("0x00010148", "ld a0, 548(a0)", "MemRead", {
            PipelineStage.FETCH: 78500, PipelineStage.DECODE: 79000,
            PipelineStage.RENAME: 79500, PipelineStage.DISPATCH: 80500,
            PipelineStage.ISSUE: 81000, PipelineStage.COMPLETE: 81500,
            PipelineStage.RETIRE: 137000
        }),
        5: ("0x00010154", "auipc a2, 1", "IntAlu", {
            PipelineStage.FETCH: 78500, PipelineStage.DECODE: 79000,
            PipelineStage.RENAME: 79500, PipelineStage.DISPATCH: 80500,
            PipelineStage.ISSUE: 80500, PipelineStage.COMPLETE: 81000,
            PipelineStage.RETIRE: 141000
        }),
        7: ("0x0001015c", "addi a3, zero, 2", "IntAlu", {
            PipelineStage.FETCH: 78500, PipelineStage.DECODE: 79000,
            PipelineStage.RENAME: 79500, PipelineStage.DISPATCH: 80500,
            PipelineStage.ISSUE: 80500, PipelineStage.COMPLETE: 81000,
            PipelineStage.RETIRE: 141500
        }),
        4: ("0x00010150", "ld a1, 548(a1)", "MemRead", {
            PipelineStage.FETCH: 78500, PipelineStage.DECODE: 79000,
            PipelineStage.RENAME: 79500, PipelineStage.DISPATCH: 80500,
            PipelineStage.ISSUE: 81000, PipelineStage.COMPLETE: 81500,
            PipelineStage.RETIRE: 141000
        }),
    }
    assert_instructions(parser, expected, all_stages)
