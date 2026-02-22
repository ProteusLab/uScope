# tests/conftest.py
import pytest
from pathlib import Path

from uScope.config import Config, load_config
from uScope.parser import PipeViewParser
from uScope.O3 import Instruction, PipelineStage


@pytest.fixture(scope="session")
def config() -> Config:
    config_dir = Path(__file__).parent.parent.joinpath("src/uScope/configs")
    return load_config(config_dir)


@pytest.fixture
def minimal_parser() -> PipeViewParser:
    parser = PipeViewParser()
    instr = Instruction(
        seq_num=1,
        pc="0x1000",
        disasm="add x1, x2, x3",
        opclass="IntAlu",
        stages={
            PipelineStage.FETCH: 1000,
            PipelineStage.DECODE: 1100,
            PipelineStage.RENAME: 1150,
            PipelineStage.DISPATCH: 1200,
            PipelineStage.ISSUE: 1300,
            PipelineStage.COMPLETE: 1400,
            PipelineStage.RETIRE: 1500,
        },
        stage_order=[
            PipelineStage.FETCH,
            PipelineStage.DECODE,
            PipelineStage.RENAME,
            PipelineStage.DISPATCH,
            PipelineStage.ISSUE,
            PipelineStage.COMPLETE,
            PipelineStage.RETIRE,
        ],
    )
    parser.instructions = {1: instr}
    return parser


@pytest.fixture
def trace_with_in_order(tmp_path: Path) -> Path:
    content = """\
O3PipeView:fetch:1000:0x1000:0:1:add x1, x2, x3:IntAlu
O3PipeView:decode:1100
O3PipeView:rename:1150
O3PipeView:dispatch:1200
O3PipeView:issue:1300
O3PipeView:complete:1400
O3PipeView:retire:1500:store:0
O3PipeView:fetch:2000:0x1004:0:2:lw a0, 0(a1):MemRead
O3PipeView:decode:2100
O3PipeView:rename:2150
O3PipeView:dispatch:2200
O3PipeView:issue:2300
O3PipeView:complete:2400
O3PipeView:retire:2500:store:0
O3PipeView:fetch:3000:0x1008:0:3:mul x10, x21, x11:IntMult
O3PipeView:decode:0
O3PipeView:rename:0
O3PipeView:dispatch:0
O3PipeView:issue:0
O3PipeView:complete:0
O3PipeView:retire:0:store:0
"""
    trace_file = tmp_path.joinpath("trace_with_in_order.out")
    trace_file.write_text(content)
    return trace_file


@pytest.fixture
def trace_with_squashed(tmp_path: Path) -> Path:
    content = """\
O3PipeView:fetch:1000:0x1000:0:1:lw a1, 4(a1):MemRead
O3PipeView:decode:0
O3PipeView:rename:0
O3PipeView:dispatch:0
O3PipeView:issue:0
O3PipeView:complete:0
O3PipeView:retire:0:store:0
O3PipeView:fetch:2000:0x1004:0:2:lw a0, 0(a1):MemRead
O3PipeView:decode:0
O3PipeView:rename:0
O3PipeView:dispatch:0
O3PipeView:issue:0
O3PipeView:complete:0
O3PipeView:retire:0:store:0
"""
    trace_file = tmp_path.joinpath("trace_with_zero.out")
    trace_file.write_text(content)
    return trace_file


@pytest.fixture
def trace_with_missing_stages(tmp_path: Path) -> Path:
    content = """\
O3PipeView:fetch:1000:0x1000:0:1:add x1, x2, x3:IntAlu
O3PipeView:decode:1100
O3PipeView:rename:1150
O3PipeView:issue:1300
O3PipeView:complete:1400
O3PipeView:retire:1500:store:0
"""
    trace_file = tmp_path.joinpath("trace_missing.out")
    trace_file.write_text(content)
    return trace_file


@pytest.fixture
def trace_with_empty_lines(tmp_path: Path) -> Path:
    content = """\
O3PipeView:fetch:1000:0x1000:0:1:add x1, x2, x3:IntAlu

O3PipeView:decode:1100

O3PipeView:rename:1150
O3PipeView:dispatch:1200
O3PipeView:issue:1300
O3PipeView:complete:1400
O3PipeView:retire:1500:store:0

O3PipeView:fetch:2000:0x2000:0:2:lw a0, 0(a1):MemRead
O3PipeView:decode:2100
O3PipeView:rename:2150
O3PipeView:dispatch:2200
O3PipeView:issue:2300
O3PipeView:complete:2400
O3PipeView:retire:2500:store:0
"""
    trace_file = tmp_path.joinpath("trace_empty_lines.out")
    trace_file.write_text(content)
    return trace_file


@pytest.fixture
def trace_with_invalid_lines(tmp_path: Path) -> Path:
    content = """\
This is a garbage line
O3PipeView:fetch:1000:0x1000:0:1:add x1, x2, x3:IntAlu
O3PipeView:decode:1100
something else
O3PipeView:rename:1150
O3PipeView:dispatch:1200
O3PipeView:issue:1300
O3PipeView:complete:1400
O3PipeView:retire:1500:store:0
"""
    trace_file = tmp_path.joinpath("trace_invalid.out")
    trace_file.write_text(content)
    return trace_file


@pytest.fixture
def trace_with_ilp(tmp_path: Path) -> Path:
    content = """\
O3PipeView:fetch:1000:0x1000:0:1:add x3, x1, x2:IntAlu
O3PipeView:decode:1100
O3PipeView:rename:1150
O3PipeView:dispatch:1200
O3PipeView:issue:1300
O3PipeView:complete:1400
O3PipeView:retire:1500:store:0
O3PipeView:fetch:1000:0x1004:0:2:add x3, x2, x4:IntAlu
O3PipeView:decode:1100
O3PipeView:rename:1150
O3PipeView:dispatch:1200
O3PipeView:issue:1300
O3PipeView:complete:1400
O3PipeView:retire:1500:store:0
"""
    trace_file = tmp_path.joinpath("trace_with_ilp.out")
    trace_file.write_text(content)
    return trace_file


@pytest.fixture
def trace_with_pipelined(tmp_path: Path) -> Path:
    content = """\
O3PipeView:fetch:137000:0x000101b4:0:53:div a7, a4, a5:IntDiv
O3PipeView:decode:137500
O3PipeView:rename:138000
O3PipeView:dispatch:139000
O3PipeView:issue:192500
O3PipeView:complete:202500
O3PipeView:retire:203500:store:0
O3PipeView:fetch:137000:0x000101b8:0:54:add s2, a6, a7:IntAlu
O3PipeView:decode:137500
O3PipeView:rename:138000
O3PipeView:dispatch:139000
O3PipeView:issue:202500
O3PipeView:complete:203000
O3PipeView:retire:204000:store:0
O3PipeView:fetch:137000:0x000101bc:0:55:sw s2, 0(a2):MemWrite
O3PipeView:decode:137500
O3PipeView:rename:138000
O3PipeView:dispatch:139000
O3PipeView:issue:203000
O3PipeView:complete:203500
O3PipeView:retire:204500:store:206500
"""
    trace_file = tmp_path.joinpath("trace_with_pipelined.out")
    trace_file.write_text(content)
    return trace_file


@pytest.fixture
def trace_with_unordered(tmp_path: Path) -> Path:
    content = """\
O3PipeView:fetch:78500:0x00010148:0:2:ld a0, 548(a0):MemRead
O3PipeView:decode:79000
O3PipeView:rename:79500
O3PipeView:dispatch:80500
O3PipeView:issue:81000
O3PipeView:complete:81500
O3PipeView:retire:137000:store:0
O3PipeView:fetch:78500:0x00010154:0:5:auipc a2, 1:IntAlu
O3PipeView:decode:79000
O3PipeView:rename:79500
O3PipeView:dispatch:80500
O3PipeView:issue:80500
O3PipeView:complete:81000
O3PipeView:retire:141000:store:0
O3PipeView:fetch:78500:0x0001015c:0:7:addi a3, zero, 2:IntAlu
O3PipeView:decode:79000
O3PipeView:rename:79500
O3PipeView:dispatch:80500
O3PipeView:issue:80500
O3PipeView:complete:81000
O3PipeView:retire:141500:store:0
O3PipeView:fetch:78500:0x00010150:0:4:ld a1, 548(a1):MemRead
O3PipeView:decode:79000
O3PipeView:rename:79500
O3PipeView:dispatch:80500
O3PipeView:issue:81000
O3PipeView:complete:81500
O3PipeView:retire:141000:store:0
"""
    trace_file = tmp_path.joinpath("trace_with_unordered.out")
    trace_file.write_text(content)
    return trace_file
