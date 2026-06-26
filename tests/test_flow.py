import pytest

from uScope.O3 import PipelineStage
from uScope.converter import ChromeTracingConverter
from uScope.parser import PipeViewParser
from uScope.events import FlowEvent
from uScope.config import Config


PIPELINE_CATS = frozenset({
    "Fetch", "Decode", "Rename", "Dispatch",
    "Issue", "Complete", "Retire", "Store Complete",
})


def assert_producers(parser, seq_num, expected, core_id=0):
    assert parser.instructions[(core_id, seq_num)].producers == expected


def find_fu_event(events, seq_num):
    return next(
        e for e in events
        if e.get("ph") == "X"
        and e.get("args", {}).get("SeqNum") == seq_num
        and e.get("cat") not in PIPELINE_CATS
    )


def assert_flow_counts(events, expected_pairs):
    s_events = [e for e in events if e.get("ph") == "s"]
    f_events = [e for e in events if e.get("ph") == "f"]
    assert len(s_events) == expected_pairs
    assert len(f_events) == expected_pairs
    return s_events, f_events


def assert_flow_paired(flow_s, flow_f):
    assert {e["id"] for e in flow_s} == {e["id"] for e in flow_f}


def assert_flows_after_fu(events, seq_num, expected_s, expected_f):
    fu = find_fu_event(events, seq_num)
    idx = events.index(fu)
    s_after = []
    f_after = []
    for j in range(idx + 1, len(events)):
        ph = events[j].get("ph")
        if ph == "s":
            s_after.append(events[j])
        elif ph == "f":
            f_after.append(events[j])
        elif ph == "X":
            break
    assert len(s_after) == expected_s
    assert len(f_after) == expected_f
    return s_after, f_after


def flow_event(**kwargs):
    kwargs.setdefault("name", "dep")
    return FlowEvent(**kwargs)


class TestParseDeps:

    def test_parse_deps(self, trace_with_deps):
        parser = PipeViewParser()
        parser.parse_file(str(trace_with_deps))

        assert_producers(parser, 1, [])
        assert_producers(parser, 2, [1])
        assert_producers(parser, 3, [1])
        assert_producers(parser, 4, [2, 3])

    def test_parse_deps_before_fetch(self):
        parser = PipeViewParser()
        parser.parse_line("O3PipeView:deps:0:2:1")
        assert parser.pending_producers[(0, 2)] == [1]

        parser.parse_line("O3PipeView:fetch:1000:0x1000:0:2:add x1,x2,x3:IntAlu")
        assert parser.current_instr.producers == [1]
        assert (0, 2) not in parser.pending_producers

        parser.parse_line("O3PipeView:fetch:2000:0x1004:0:3:add x4,x5,x6:IntAlu")
        assert_producers(parser, 2, [1])

    def test_parse_deps_line(self):
        parser = PipeViewParser()
        core, seq, prods = parser._parse_deps_line("0:42:1,2,3")
        assert core == 0
        assert seq == 42
        assert prods == [1, 2, 3]

        core, seq, prods = parser._parse_deps_line("0:5:")
        assert core == 0
        assert seq == 5
        assert prods == []

    def test_parse_memdeps_merge(self, trace_with_deps_and_memdeps):
        parser = PipeViewParser()
        parser.parse_file(str(trace_with_deps_and_memdeps))

        assert_producers(parser, 3, [1, 2])
        assert_producers(parser, 1, [])
        assert_producers(parser, 2, [1])

    def test_parse_memdeps_before_fetch(self):
        parser = PipeViewParser()
        parser.parse_line("O3PipeView:deps:0:3:1")
        parser.parse_line("O3PipeView:memdeps:0:3:2")
        assert parser.pending_producers[(0, 3)] == [1, 2]

        parser.parse_line("O3PipeView:fetch:3000:0x1008:0:3:lw x2,0(a0):MemRead")
        assert parser.current_instr.producers == [1, 2]

        parser.parse_line("O3PipeView:fetch:4000:0x100c:0:4:add x7,x8,x9:IntAlu")
        assert_producers(parser, 3, [1, 2])

    def test_parse_memdeps_only(self):
        parser = PipeViewParser()
        parser.parse_line("O3PipeView:memdeps:0:5:4")
        assert parser.pending_producers[(0, 5)] == [4]

        parser.parse_line("O3PipeView:fetch:1000:0x1000:0:5:lw x5,0(a0):MemRead")
        assert parser.current_instr.producers == [4]

        parser.parse_line("O3PipeView:fetch:2000:0x1004:0:6:add x7,x8,x9:IntAlu")
        assert_producers(parser, 5, [4])


class TestFlowEvents:

    def test_minimal(self):
        e = flow_event(ph="s", id="1", bp="e", pid=200, tid=0, ts=100)
        d = e.to_dict()
        assert d["name"] == "dep"
        assert d["ph"] == "s"
        assert d["id"] == "1"
        assert d["bp"] == "e"
        assert d["pid"] == 200
        assert d["ts"] == 100
        assert "cat" not in d
        assert "cname" not in d

    def test_with_cat(self):
        e = flow_event(ph="f", id="42", bp="e", pid=201, tid=1, ts=200,
                       cat="ReadPort", cname="cq_build_attempt")
        d = e.to_dict()
        assert d["cat"] == "ReadPort"
        assert d["cname"] == "cq_build_attempt"
        assert d["ph"] == "f"

    def test_none_omitted(self):
        e = flow_event(ph="s", id="1", bp="e", pid=200, ts=100)
        d = e.to_dict()
        assert "tid" not in d


class TestConverterFlows:

    def test_interleaving(self, trace_with_deps, config: Config):
        parser = PipeViewParser()
        parser.parse_file(str(trace_with_deps))
        converter = ChromeTracingConverter(parser, config)
        events = converter.convert()

        flow_s, flow_f = assert_flow_counts(events, 4)

        for fe in flow_s:
            idx = events.index(fe)
            prev_x = next(e for e in reversed(events[:idx])
                          if e.get("ph") == "X" and e.get("pid") == fe["pid"])
            assert prev_x["pid"] == fe["pid"]

    def test_multiple_producers(self, trace_with_deps, config: Config):
        parser = PipeViewParser()
        parser.parse_file(str(trace_with_deps))
        converter = ChromeTracingConverter(parser, config)
        events = converter.convert()

        flow_s, flow_f = assert_flow_counts(events, 4)
        assert_flow_paired(flow_s, flow_f)

        assert_flows_after_fu(events, 4, expected_s=0, expected_f=2)
        assert_flows_after_fu(events, 1, expected_s=2, expected_f=0)

    def test_cat_from_producer(self, trace_with_deps, config: Config):
        parser = PipeViewParser()
        parser.parse_file(str(trace_with_deps))
        converter = ChromeTracingConverter(parser, config)
        events = converter.convert()

        flow_s = [e for e in events if e.get("ph") == "s"]
        flow_f = [e for e in events if e.get("ph") == "f"]

        for s in flow_s:
            assert "cat" in s
            assert "cname" in s
            f = next(e for e in flow_f if e["id"] == s["id"])
            assert s["cat"] == f["cat"]

    def test_excluded_exec(self, trace_with_deps, config: Config):
        parser = PipeViewParser()
        parser.parse_file(str(trace_with_deps))
        converter = ChromeTracingConverter(parser, config, exclude_exec=True)
        events = converter.convert()

        assert not [e for e in events if e.get("ph") in ("s", "f")]

    def test_exclude_flow_flag(self, trace_with_deps, config: Config):
        parser = PipeViewParser()
        parser.parse_file(str(trace_with_deps))
        converter = ChromeTracingConverter(parser, config, exclude_flow=True)
        events = converter.convert()

        assert not [e for e in events if e.get("ph") in ("s", "f")]
