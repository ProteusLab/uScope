from typing import Dict, List, Tuple

from tqdm import tqdm

from .O3 import PipelineStage, Instruction
from .events import MetadataEvent, DurationEvent
from .thread_pool import ThreadPoolManager
from .config import IConfig
from .parser import PipeViewParser


class ChromeTracingConverter:
    def __init__(
        self,
        parser: PipeViewParser,
        config: IConfig,
        exclude_exec: bool = False,
        exclude_pipeline: bool = False,
        only_committed: bool = False,
        store_completions: bool = True,
    ):
        self.parser: PipeViewParser = parser
        if not isinstance(config, IConfig):
            raise TypeError(
                f"Unexpected Config type {type(config).__name__}. "
                f"Please derive your configuration class from {IConfig}"
            )
        self.config: IConfig = config

        self.exclude_exec: bool = exclude_exec
        self.exclude_pipeline: bool = exclude_pipeline
        self.only_committed: bool = only_committed
        self.store_completions: bool = store_completions

        self.metadata_events: List[MetadataEvent] = []
        self.duration_events: List[DurationEvent] = []

        self.stage_managers: Dict[PipelineStage, ThreadPoolManager] = {}
        self.func_units_managers: Dict[str, ThreadPoolManager] = {}
        self.store_thread_pool: ThreadPoolManager = None

    def convert(self, progress: bool = True) -> List[dict]:
        self._add_metadata()
        instructions = self.instructions_by_seq_num()
        for instr in tqdm(
            instructions,
            desc="Converting",
            unit="instr",
            disable=not progress,
            leave=False,
        ):
            if self.only_committed and instr.is_squashed:
                continue
            if not self.exclude_pipeline:
                self._add_pipeline_stage_events(instr)
            if not self.exclude_exec:
                self._add_execution_unit_events(instr)
            if self.store_completions and instr.store_tick > 0:
                self._add_store_completion_event(instr)

        return [e.to_dict() for e in self.metadata_events + self.duration_events]

    def instructions_by_seq_num(self):
        return sorted(self.parser.instructions.values(), key=lambda x: x.seq_num)

    def _add_metadata(self):
        if not self.exclude_pipeline:
            self._add_pipeline_stages_metadata()
        if not self.exclude_exec:
            self._add_execution_units_metadata()
        if self.store_completions:
            self._add_store_completions_metadata()

    def _add_pipeline_stages_metadata(self):
        for id, stage in enumerate(PipelineStage.order()):
            stage_name = self.config.get_stage_name(stage)
            process_name = f"{(id + 1):02d}_{stage_name}"
            pid = self.config.pipeline_pid + id

            manager = ThreadPoolManager(
                max_width=self.config.pipeline_width,
                pid=pid,
                thread_name_prefix=stage_name,
                metadata_events=self.metadata_events
            )

            self.stage_managers[stage] = manager
            manager.add_initial_thread(0)

            self.metadata_events.append(MetadataEvent(
                name="process_name", pid=pid,
                args={"name": process_name}
            ))

            self.metadata_events.append(MetadataEvent(
                name="thread_name", pid=pid, tid=0,
                args={"name": f"00_{stage_name}"}
            ))

            self.metadata_events.append(MetadataEvent(
                name="thread_sort_index", pid=pid, tid=0,
                args={"sort_index": 0}
            ))

    def _add_execution_units_metadata(self):
        unit_names = set()
        for instr in self.instructions_by_seq_num():
            if instr.opclass:
                unit_names.add(self.config.get_func_unit(instr.opclass))

        for i, unit_name in enumerate(sorted(unit_names)):
            pid = self.config.func_units_pid + i

            manager = ThreadPoolManager(
                max_width=self.config.func_units_width,
                pid=pid,
                thread_name_prefix=unit_name,
                metadata_events=self.metadata_events
            )
            self.func_units_managers[unit_name] = manager
            manager.add_initial_thread(0)

            self.metadata_events.append(MetadataEvent(
                name="process_name", pid=pid,
                args={"name": f"{unit_name}"}
            ))

            self.metadata_events.append(MetadataEvent(
                name="thread_name", pid=pid, tid=0,
                args={"name": f"00_{unit_name}"}
            ))

            self.metadata_events.append(MetadataEvent(
                name="thread_sort_index", pid=pid, tid=0,
                args={"sort_index": 0}
            ))

    def _assign_thread_for_stage(self, stage: PipelineStage, start_time: int, end_time: int) -> Tuple[int, int]:
        return self.stage_managers[stage].assign_thread(start_time, end_time)

    def _assign_thread_for_func_units(self, unit_name: str, start_time: int, end_time: int) -> Tuple[int, int]:
        return self.func_units_managers[unit_name].assign_thread(start_time, end_time)

    def _add_pipeline_stage_events(self, instr : Instruction):
        mnemonic = instr.mnemonic
        cname = self.config.get_squashed_cname() if instr.is_squashed else self.config.get_color_for_instr(instr)

        active = [(st, instr.stages[st]) for st in instr.stage_order if instr.stages.get(st, 0) > 0]
        if not active:
            return
        active.sort(key=lambda x: x[1])

        for i, (stage, tick) in enumerate(active):
            dur = max(1, active[i + 1][1] - tick) if i < len(active) - 1 else 1
            start, end = tick, tick + dur
            pid, tid = self._assign_thread_for_stage(stage, start, end)

            self.duration_events.append(DurationEvent(
                name=mnemonic,
                cat=self.config.get_stage_name(stage),
                ts=tick,
                dur=dur,
                pid=pid,
                tid=tid,
                cname=cname,
                args={
                    "PC": instr.pc,
                    "SeqNum": instr.seq_num,
                    "Stage": self.config.get_stage_name(stage),
                    "OpClass": instr.opclass,
                    "Disasm": instr.disasm
                }
            ))

    def _add_execution_unit_events(self, instr : Instruction):
        if not instr.opclass:
            return

        mnemonic = instr.mnemonic

        issue = instr.stages.get(PipelineStage.ISSUE, 0)
        complete = instr.stages.get(PipelineStage.COMPLETE, 0)
        if issue <= 0 or complete <= 0 or issue >= complete:
            return

        unit = self.config.get_func_unit(instr.opclass)
        if unit not in self.func_units_managers:
            return

        pid, tid = self._assign_thread_for_func_units(unit, issue, complete)
        dur = complete - issue
        cname = self.config.get_squashed_cname() if instr.is_squashed else self.config.get_color_for_instr(instr)

        self.duration_events.append(DurationEvent(
            name=mnemonic,
            cat=unit,
            ts=issue,
            dur=dur,
            pid=pid,
            tid=tid,
            cname=cname,
            args={
                "PC": instr.pc,
                "SeqNum": instr.seq_num,
                "OpClass": instr.opclass,
                "Unit": unit,
                "Duration": dur,
                "Disasm": instr.disasm
            }
        ))

    def _add_store_completions_metadata(self):
        store_name = self.config.get_stage_name(PipelineStage.STORE_COMPLETE)
        pid = self.config.store_completions_pid

        manager = ThreadPoolManager(
            max_width=self.config.pipeline_width,
            pid=pid,
            thread_name_prefix=store_name,
            metadata_events=self.metadata_events,
        )
        self.store_thread_pool = manager
        manager.add_initial_thread(0)

        self.metadata_events.append(
            MetadataEvent(
                name="process_name",
                pid=pid,
                args={"name": store_name},
            )
        )
        self.metadata_events.append(
            MetadataEvent(
                name="thread_name",
                pid=pid,
                tid=0,
                args={"name": f"00_{store_name}"},
            )
        )
        self.metadata_events.append(
            MetadataEvent(
                name="thread_sort_index",
                pid=pid,
                tid=0,
                args={"sort_index": 0},
            )
        )

    def _add_store_completion_event(self, instr: Instruction):
        retire_tick = instr.stages.get(PipelineStage.RETIRE, 0)
        store_tick = instr.store_tick
        if retire_tick <= 0 or store_tick <= 0 or store_tick <= retire_tick:
            return

        mnemonic = instr.mnemonic
        store_name = self.config.get_stage_name(PipelineStage.STORE_COMPLETE)

        pid = self.config.store_completions_pid
        tid = 0
        if self.store_thread_pool is not None:
            _, tid = self.store_thread_pool.assign_thread(retire_tick, store_tick)

        dur = store_tick - retire_tick
        cname = self.config.get_squashed_cname() if instr.is_squashed else self.config.get_color_for_instr(instr)

        self.duration_events.append(
            DurationEvent(
                name=mnemonic,
                cat=store_name,
                ts=retire_tick,
                dur=dur,
                pid=pid,
                tid=tid,
                cname=cname,
                args={
                    "PC": instr.pc,
                    "SeqNum": instr.seq_num,
                    "OpClass": instr.opclass,
                    "Stage": store_name,
                    "Duration": dur,
                    "Disasm": instr.disasm,
                },
            )
        )
