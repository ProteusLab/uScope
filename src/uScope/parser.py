from .O3 import Instruction, PipelineStage


class PipeViewParser:
    PREFIX = "O3PipeView:"

    def __init__(self):
        self.instructions = {}
        self.current_core_id = None
        self.current_seq_num = None
        self.current_instr = None
        self.stage_map = {f"{stage}": stage for stage in PipelineStage.order()}

    def parse_file(self, filename: str):
        with open(filename, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    self.parse_line(line)

        if self.current_instr is not None:
            self.instructions[(self.current_core_id, self.current_seq_num)] = self.current_instr

        self.instructions = {
            key: instr
            for key, instr in self.instructions.items()
            if any(tick > 0 for tick in instr.stages.values())
        }

    def get_core_ids(self):
        return sorted(set(instr.core_id for instr in self.instructions.values()))

    @staticmethod
    def _parse_fetch_line(rest: str):
        parts = rest.split(":", 5)
        if len(parts) != 6:
            return None
        tick_str, pc, core_id_str, seq_str, disasm, opclass = parts
        return int(tick_str), pc, int(core_id_str), int(seq_str), disasm.strip(), opclass.strip()

    @staticmethod
    def _parse_stage_line(rest: str):
        idx = rest.index(":")
        stage_name = rest[:idx]
        rest = rest[idx + 1 :]
        idx = rest.find(":")
        if idx == -1:
            tick = int(rest)
            store_tick = 0
        else:
            tick = int(rest[:idx])
            remaining = rest[idx + 1 :]
            if remaining.startswith("store:"):
                store_tick = int(remaining[6:])
            else:
                store_tick = 0
        return stage_name, tick, store_tick

    def parse_line(self, line: str):
        if not line.startswith(self.PREFIX):
            return

        rest = line[len(self.PREFIX) :]

        if rest.startswith("fetch:"):
            result = self._parse_fetch_line(rest[6:])
            if result is None:
                return
            tick, pc, core_id, seq_num, disasm, opclass = result

            if self.current_instr is not None:
                self.instructions[(self.current_core_id, self.current_seq_num)] = self.current_instr

            self.current_core_id = core_id
            self.current_seq_num = seq_num
            self.current_instr = Instruction(
                seq_num=seq_num,
                pc=pc,
                disasm=disasm,
                opclass=opclass,
                stages={},
                stage_order=[],
                core_id=core_id,
            )

            self.current_instr.stages[PipelineStage.FETCH] = tick
            self.current_instr.stage_order.append(PipelineStage.FETCH)
            return

        if self.current_instr is not None:
            stage_name, tick, store_tick = self._parse_stage_line(rest)
            stage_name = stage_name.lower()

            if stage_name in self.stage_map:
                stage = self.stage_map[stage_name]
                self.current_instr.stages[stage] = tick

                if stage not in self.current_instr.stage_order:
                    self.current_instr.stage_order.append(stage)

            if stage_name == PipelineStage.RETIRE.value and store_tick > 0:
                self.current_instr.store_tick = store_tick
