import pytest

from uScope.thread_pool import ThreadPoolManager


def test_reuse_existing_thread():
    metadata = []
    manager = ThreadPoolManager(
        max_width=2, pid=100, thread_name_prefix="Test", metadata_events=metadata
    )
    manager.add_initial_thread(end_time=10)

    pid, tid = manager.assign_thread(start_time=15, end_time=20)

    assert pid == 100 and tid == 0
    assert manager.pool[0][0] == 20
    assert len(metadata) == 0


def test_assign_new_thread():
    metadata = []
    manager = ThreadPoolManager(
        max_width=2, pid=100, thread_name_prefix="Test", metadata_events=metadata
    )
    manager.add_initial_thread(end_time=10)
    pid, tid = manager.assign_thread(start_time=5, end_time=15)

    assert pid == 100 and tid == 1
    assert len(manager.pool) == 2
    assert len(metadata) == 2
    assert metadata[0].tid == 1 and metadata[0].args["name"] == "01_Test"
    assert metadata[1].tid == 1 and metadata[1].args["sort_index"] == 2


def test_reuse_earliest_thread():
    metadata = []
    manager = ThreadPoolManager(
        max_width=2, pid=100, thread_name_prefix="Test", metadata_events=metadata
    )
    manager.add_initial_thread(end_time=10)
    manager.assign_thread(start_time=5, end_time=20)

    pid, tid = manager.assign_thread(start_time=8, end_time=25)

    assert tid == 0
    assert pid == 100
    assert manager.pool[0][0] == 25
    assert manager.pool[1][0] == 20
