from typing import List, Tuple

from .events import MetadataEvent

class ThreadPoolManager:
    def __init__(self, max_width: int, pid: int, thread_name_prefix: str,
                 metadata_events: List[MetadataEvent]):
        self.max_width = max_width
        self.pid = pid
        self.thread_name_prefix = thread_name_prefix
        self.metadata_events = metadata_events

        self.pool: List[Tuple[int, int]] = []
        self.next_tid = 0

    def add_initial_thread(self, end_time: int = 0):
        self.pool.append((end_time, 0))
        self.next_tid = 1

    def get_or_create_thread(self, start_time: int, end_time: int) -> Tuple[int, int]:
        for i, (last_end, tid) in enumerate(self.pool):
            if last_end <= start_time:
                self.pool[i] = (end_time, tid)
                return self.pid, tid

        if len(self.pool) < self.max_width:
            new_tid = self.next_tid
            self.next_tid += 1
            self.pool.append((end_time, new_tid))

            self.metadata_events.append(MetadataEvent(
                name="thread_name", pid=self.pid, tid=new_tid,
                args={"name": f"{new_tid:02d}_{self.thread_name_prefix}"}
            ))
            self.metadata_events.append(MetadataEvent(
                name="thread_sort_index", pid=self.pid, tid=new_tid,
                args={"sort_index": new_tid + 1}
            ))
            return self.pid, new_tid

        earliest_idx = min(range(len(self.pool)), key=lambda i: self.pool[i][0])
        earliest_end, tid = self.pool[earliest_idx]
        self.pool[earliest_idx] = (end_time, tid)
        return self.pid, tid
