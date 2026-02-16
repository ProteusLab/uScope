from typing import Dict, List, Tuple

from .O3 import PipelineStage, Instruction, OpClass
from .utils import stable_hash
from .events import MetadataEvent, DurationEvent
from .thread_pool import ThreadPoolManager
from .config import Config

class ChromeTracingConverter:
    def __init__(self, parser, config : Config):
        self.parser = parser
        self.config = config
        self.metadata_events: List[MetadataEvent] = []
        self.duration_events: List[DurationEvent] = []

        settings = config.settings
        self.FU_units = config.FU_units
        self.colors = config.colors

        self.PID_PIPELINE_STAGES_BASE = settings.PID_PIPELINE_STAGES_BASE
        self.PID_EXECUTION_UNITS_BASE = settings.PID_EXECUTION_UNITS_BASE
        self.MAX_PIPE_WIDTH = settings.MAX_PIPE_WIDTH
        self.MAX_EXEC_UNIT_WIDTH = settings.MAX_EXEC_UNIT_WIDTH

        self.default_colors = self.colors.default
        self.stage_names = config.stage_names

        self.stage_managers: Dict[PipelineStage, ThreadPoolManager] = {}
        self.exec_unit_managers: Dict[str, ThreadPoolManager] = {}

    def convert(self) -> List[dict]:
        self._add_metadata()
        for instr in self.instructions_by_seq_num():
            self._add_pipeline_stage_events(instr)
            self._add_execution_unit_events(instr)

        return [e.to_dict() for e in self.metadata_events + self.duration_events]

    def instructions_by_seq_num(self):
        return sorted(self.parser.instructions.values(), key=lambda x: x.seq_num)

    def _opclass_to_unit(self, opclass: str) -> str:
        return self.FU_units.get(opclass, OpClass.No_OpClass.value)

    def _get_cname_for_instruction(self, instr : Instruction) -> str:
        opclass = instr.opclass or 'Unknown'
        unit = self._opclass_to_unit(opclass)
        family = self.colors.get(unit, self.default_colors)
        idx = stable_hash(instr.mnemonic, len(family))
        return family[idx]

    def _add_metadata(self):
        self._add_pipeline_stages_metadata()
        self._add_execution_units_metadata()

    def _add_pipeline_stages_metadata(self):
        stage_order = [
            PipelineStage.FETCH, PipelineStage.DECODE, PipelineStage.RENAME,
            PipelineStage.DISPATCH, PipelineStage.ISSUE,
            PipelineStage.COMPLETE, PipelineStage.RETIRE
        ]

        for id, stage in enumerate(stage_order):
            stage_name = self.stage_names[stage.value]
            process_name = f"{(id + 1):02d}_{stage_name}"
            pid = self.PID_PIPELINE_STAGES_BASE + id

            manager = ThreadPoolManager(
                max_width=self.MAX_PIPE_WIDTH,
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
                unit_names.add(self._opclass_to_unit(instr.opclass))

        for i, unit_name in enumerate(sorted(unit_names)):
            pid = self.PID_EXECUTION_UNITS_BASE + i

            manager = ThreadPoolManager(
                max_width=self.MAX_EXEC_UNIT_WIDTH,
                pid=pid,
                thread_name_prefix=unit_name,
                metadata_events=self.metadata_events
            )
            self.exec_unit_managers[unit_name] = manager
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

    def _assign_thread_for_exec_unit(self, unit_name: str, start_time: int, end_time: int) -> Tuple[int, int]:
        return self.exec_unit_managers[unit_name].assign_thread(start_time, end_time)

    def _add_pipeline_stage_events(self, instr : Instruction):
        mnemonic = instr.mnemonic
        cname = self._get_cname_for_instruction(instr)

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
                cat=self.stage_names[stage.value],
                ts=tick,
                dur=dur,
                pid=pid,
                tid=tid,
                cname=cname,
                args={
                    "PC": instr.pc,
                    "SeqNum": instr.seq_num,
                    "Stage": self.stage_names[stage.value],
                    "OpClass": instr.opclass,
                    "Mnemonic": mnemonic
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

        unit = self._opclass_to_unit(instr.opclass)
        if unit not in self.exec_unit_managers:
            return

        pid, tid = self._assign_thread_for_exec_unit(unit, issue, complete)
        dur = complete - issue

        self.duration_events.append(DurationEvent(
            name=mnemonic,
            cat=unit,
            ts=issue,
            dur=dur,
            pid=pid,
            tid=tid,
            cname=self._get_cname_for_instruction(instr),
            args={
                "PC": instr.pc,
                "SeqNum": instr.seq_num,
                "OpClass": instr.opclass,
                "Unit": unit,
                "Duration": dur,
                "Mnemonic": mnemonic
            }
        ))
