import pytest
from typing import List, Tuple

from uScope.O3 import PipelineStage
from uScope.converter import ChromeTracingConverter
from uScope.parser import PipeViewParser
from uScope.config import Config


def filter_events_by_stage(events: List[dict], config: Config, stage: PipelineStage) -> List[dict]:
    stage_name = config.get_stage_name(stage)
    return [e for e in events if e.get("cat") == stage_name]

def assert_stage_events(events: List[dict], config: Config, stage: PipelineStage,
                        expected_tuples: List[Tuple[int, int]]):
    stage_events = filter_events_by_stage(events, config, stage)
    assert len(stage_events) == len(expected_tuples), \
        f"Stage {stage.name}: expected {len(expected_tuples)} events, got {len(stage_events)}"

    for i, (event, (exp_ts, exp_dur)) in enumerate(zip(stage_events, expected_tuples)):
        assert event["ts"] == exp_ts, f"Stage {stage.name}, event {i}: ts mismatch"
        assert event["dur"] == exp_dur, f"Stage {stage.name}, event {i}: dur mismatch"


def assert_seq_nums(events: List[dict], expected_seq_nums: List[int]):
    dur_events = [e for e in events if e.get("ph") == "X"]
    seq_nums = set()
    for e in dur_events:
        args = e.get("args", {})
        if "SeqNum" in args:
            seq_nums.add(args["SeqNum"])
    for seq in expected_seq_nums:
        assert seq in seq_nums, f"SeqNum {seq} not found in duration events"


def test_func_units_metadata(minimal_parser, config : Config):
    converter = ChromeTracingConverter(minimal_parser, config)
    converter._add_metadata()

    found = False
    for e in converter.metadata_events:
        if e.name == "process_name" and e.args.get("name") == "IntALU":
            found = True
            break
    assert found, "Process for IntALU not found"


def test_convert_minimal_parser(minimal_parser, config : Config):
    converter = ChromeTracingConverter(minimal_parser, config)
    events = converter.convert()

    assert len(events) > 0

    assert_stage_events(events, config, PipelineStage.FETCH, [(1000, 100)])
    assert_stage_events(events, config, PipelineStage.DECODE, [(1100, 50)])
    assert_stage_events(events, config, PipelineStage.RENAME, [(1150, 50)])
    assert_stage_events(events, config, PipelineStage.DISPATCH, [(1200, 100)])
    assert_stage_events(events, config, PipelineStage.ISSUE, [(1300, 100)])
    assert_stage_events(events, config, PipelineStage.COMPLETE, [(1400, 100)])


def test_convert_in_order(trace_with_in_order, config : Config):
    parser = PipeViewParser()
    parser.parse_file(str(trace_with_in_order))

    converter = ChromeTracingConverter(parser, config)
    events = converter.convert()

    assert_stage_events(events, config, PipelineStage.FETCH, [
        (1000, 100),
        (2000, 100),
        (3000, 1)
    ])
    assert_stage_events(events, config, PipelineStage.DECODE, [
        (1100, 50),
        (2100, 50)
    ])
    assert_stage_events(events, config, PipelineStage.RENAME, [
        (1150, 50),
        (2150, 50)
    ])
    assert_stage_events(events, config, PipelineStage.DISPATCH, [
        (1200, 100),
        (2200, 100)
    ])
    assert_stage_events(events, config, PipelineStage.ISSUE, [
        (1300, 100),
        (2300, 100)
    ])
    assert_stage_events(events, config, PipelineStage.COMPLETE, [
        (1400, 100),
        (2400, 100)
    ])
    assert_stage_events(events, config, PipelineStage.RETIRE, [
        (1500, 1),
        (2500, 1)
    ])

    assert_seq_nums(events, [1, 2, 3])


def test_convert_ilp(trace_with_ilp, config : Config):
    parser = PipeViewParser()
    parser.parse_file(str(trace_with_ilp))

    converter = ChromeTracingConverter(parser, config)
    events = converter.convert()

    assert_stage_events(events, config, PipelineStage.FETCH, [
        (1000, 100),
        (1000, 100)
    ])
    assert_stage_events(events, config, PipelineStage.DECODE, [
        (1100, 50),
        (1100, 50)
    ])
    assert_stage_events(events, config, PipelineStage.RENAME, [
        (1150, 50),
        (1150, 50)
    ])
    assert_stage_events(events, config, PipelineStage.DISPATCH, [
        (1200, 100),
        (1200, 100)
    ])
    assert_stage_events(events, config, PipelineStage.ISSUE, [
        (1300, 100),
        (1300, 100)
    ])
    assert_stage_events(events, config, PipelineStage.COMPLETE, [
        (1400, 100),
        (1400, 100)
    ])
    assert_stage_events(events, config, PipelineStage.RETIRE, [
        (1500, 1),
        (1500, 1)
    ])

    assert_seq_nums(events, [1, 2])


def test_convert_pipelined(trace_with_pipelined, config : Config):
    parser = PipeViewParser()
    parser.parse_file(str(trace_with_pipelined))

    converter = ChromeTracingConverter(parser, config)
    events = converter.convert()

    assert_stage_events(events, config, PipelineStage.FETCH, [
        (137000, 500),
        (137000, 500),
        (137000, 500)
    ])
    assert_stage_events(events, config, PipelineStage.DECODE, [
        (137500, 500),
        (137500, 500),
        (137500, 500)
    ])
    assert_stage_events(events, config, PipelineStage.RENAME, [
        (138000, 1000),
        (138000, 1000),
        (138000, 1000)
    ])
    assert_stage_events(events, config, PipelineStage.DISPATCH, [
        (139000, 53500),
        (139000, 63500),
        (139000, 64000)
    ])
    assert_stage_events(events, config, PipelineStage.ISSUE, [
        (192500, 10000),
        (202500, 500),
        (203000, 500)
    ])
    assert_stage_events(events, config, PipelineStage.COMPLETE, [
        (202500, 1000),
        (203000, 1000),
        (203500, 1000)
    ])
    assert_stage_events(events, config, PipelineStage.RETIRE, [
        (203500, 1),
        (204000, 1),
        (204500, 1)
    ])

    assert_seq_nums(events, [53, 54, 55])


def test_convert_unordered(trace_with_unordered, config : Config):
    parser = PipeViewParser()
    parser.parse_file(str(trace_with_unordered))

    converter = ChromeTracingConverter(parser, config)
    events = converter.convert()

    assert_stage_events(events, config, PipelineStage.FETCH, [
        (78500, 500),
        (78500, 500),
        (78500, 500),
        (78500, 500)
    ])

    assert_stage_events(events, config, PipelineStage.DECODE, [
        (79000, 500),
        (79000, 500),
        (79000, 500),
        (79000, 500)
    ])

    assert_stage_events(events, config, PipelineStage.RENAME, [
        (79500, 1000),
        (79500, 1000),
        (79500, 1000),
        (79500, 1000)
    ])

    assert_stage_events(events, config, PipelineStage.DISPATCH, [
        (80500, 500),
        (80500, 500),
        (80500, 1),
        (80500, 1),
    ])

    assert_stage_events(events, config, PipelineStage.ISSUE, [
        (81000, 500),
        (81000, 500),
        (80500, 500),
        (80500, 500),
    ])

    assert_stage_events(events, config, PipelineStage.COMPLETE, [
        (81500, 55500),
        (81500, 59500),
        (81000, 60000),
        (81000, 60500),
    ])

    assert_stage_events(events, config, PipelineStage.RETIRE, [
        (137000, 1),
        (141000, 1),
        (141000, 1),
        (141500, 1)
    ])

    assert_seq_nums(events, [2, 4, 5, 7])
