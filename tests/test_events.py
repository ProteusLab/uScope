import pytest
from typing import List, Dict, Any

from uScope.O3 import PipelineStage, OpClass
from uScope.converter import ChromeTracingConverter
from uScope.parser import PipeViewParser
from uScope.config import Config


def filter_events_by_category(events: List[dict], config: Config, category: Any) -> List[dict]:
    if isinstance(category, PipelineStage):
        category_name = config.get_stage_name(category)
    elif isinstance(category, OpClass):
        category_name = config.get_func_unit(category)
    else:
        assert False, f"Unsupported category {type(category).__name__} type"
    return [e for e in events if e.get("cat") == category_name]

def assert_duration_events(events: List[dict], config: Config, stage: PipelineStage,
                        expected_data: List[Dict]):
    filtered_events = filter_events_by_category(events, config, stage)
    assert len(filtered_events) == len(expected_data), \
        f"Stage {stage.name}: expected {len(expected_data)} events, got {len(filtered_events)}"

    for (converted, expected) in zip(filtered_events, expected_data):
        for name in expected.keys():
            assert converted[name] == expected[name]

def test_convert_in_order(trace_with_in_order, config : Config):
    parser = PipeViewParser()
    parser.parse_file(str(trace_with_in_order))

    converter = ChromeTracingConverter(parser, config)
    events = converter.convert()

    assert_duration_events(events, config, PipelineStage.FETCH, [
        { "name" : "ADD", "ts" : 1000, "dur" : 100, "pid" : 100, "tid" : 0  },
        { "name" : "LW", "ts" : 2000, "dur" : 100, "pid" : 100, "tid" : 0 },
        { "name" : "MUL", "ts" : 3000, "dur" : 1, "pid" : 100, "tid" : 0   }
    ])
    assert_duration_events(events, config, PipelineStage.DECODE, [
        { "name" : "ADD", "ts" : 1100, "dur" : 50, "pid" : 101, "tid" : 0  },
        { "name" : "LW", "ts" : 2100, "dur" : 50, "pid" : 101, "tid" : 0  }
    ])
    assert_duration_events(events, config, PipelineStage.RENAME, [
        { "name" : "ADD", "ts" : 1150, "dur" : 50, "pid" : 102, "tid" : 0 },
        { "name" : "LW", "ts" : 2150, "dur" : 50, "pid" : 102, "tid" : 0 }
    ])
    assert_duration_events(events, config, PipelineStage.DISPATCH, [
        { "name" : "ADD", "ts" : 1200, "dur" : 100, "pid" : 103, "tid" : 0 },
        { "name" : "LW", "ts" : 2200, "dur" : 100, "pid" : 103, "tid" : 0 }
    ])
    assert_duration_events(events, config, PipelineStage.ISSUE, [
        { "name" : "ADD", "ts" : 1300, "dur" : 100, "pid" : 104, "tid" : 0 },
        { "name" : "LW", "ts" : 2300, "dur" : 100, "pid" : 104, "tid" : 0 }
    ])
    assert_duration_events(events, config, PipelineStage.COMPLETE, [
        { "name" : "ADD", "ts" : 1400, "dur" : 100, "pid" : 105, "tid" : 0 },
        { "name" : "LW", "ts" : 2400, "dur" : 100, "pid" : 105, "tid" : 0 }
    ])
    assert_duration_events(events, config, PipelineStage.RETIRE, [
        { "name" : "ADD", "ts" : 1500, "dur" : 1, "pid" : 106, "tid" : 0 },
        { "name" : "LW", "ts" : 2500, "dur" : 1, "pid" : 106 , "tid" : 0 }
    ])

    # TODO: Test Func Units Events
