import pytest

from uScope.thread_pool import StageLaneManager


def test_reuse_existing_lane():
    metadata = []
    manager = StageLaneManager(
        max_width=2, pid=100, lane_name_prefix="Test", metadata_events=metadata
    )

    pid, tid = manager.assign_lane(start_time=15, end_time=20)

    assert pid == 100 and tid == 0
    assert manager.pool[0][0] == 20


def test_assign_new_lane():
    metadata = []
    manager = StageLaneManager(
        max_width=2, pid=100, lane_name_prefix="Test", metadata_events=metadata
    )
    manager.assign_lane(start_time=0, end_time=10)

    pid, tid = manager.assign_lane(start_time=5, end_time=15)

    assert pid == 100 and tid == 1
    assert len(manager.pool) == 2
    assert len(metadata) == 4
    assert metadata[2].tid == 1 and metadata[2].args["name"] == "01_Test"
    assert metadata[3].tid == 1 and metadata[3].args["sort_index"] == 2


def test_reuse_earliest_lane():
    metadata = []
    manager = StageLaneManager(
        max_width=2, pid=100, lane_name_prefix="Test", metadata_events=metadata
    )
    manager.assign_lane(start_time=0, end_time=5)
    manager.assign_lane(start_time=0, end_time=10)

    pid, tid = manager.assign_lane(start_time=3, end_time=20)

    assert tid == 0
    assert pid == 100
    assert manager.pool[0][0] == 20
    assert manager.pool[1][0] == 10
