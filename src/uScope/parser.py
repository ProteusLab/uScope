from .O3 import Instruction, PipelineStage


class PipeViewParser:
    PREFIX = "O3PipeView:"
    USCOPE_PREFIX = "uScopeView:"

    def __init__(self):
        self.instructions = {}
        self.current_core_id = None
        self.current_seq_num = None
        self.current_instr = None
        self.stage_map = {f"{stage}": stage for stage in PipelineStage.order()}
        self.pending_producers = {}

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
        if len(parts) < 5:
            return None
        tick_str, pc, pos2, seq_str, disasm = parts[:5]
        opclass = parts[5].strip() if len(parts) > 5 else ""
        return int(tick_str), pc, int(pos2), int(seq_str), disasm.strip(), opclass

    @staticmethod
    def _parse_usinfo_line(rest: str):
        parts = rest.split(":", 2)
        if len(parts) != 3:
            return None
        return int(parts[0]), int(parts[1]), parts[2].strip()

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

    @staticmethod
    def _parse_deps_line(rest: str):
        first = rest.index(":")
        core_id = int(rest[:first])
        rest = rest[first + 1 :]
        second = rest.index(":")
        seq_num = int(rest[:second])
        producers_str = rest[second + 1 :]
        if producers_str:
            producers = [int(p) for p in producers_str.split(",")]
        else:
            producers = []
        return core_id, seq_num, producers

    def _apply_producers(self, core_id, seq_num, producers):
        instr = self.instructions.get((core_id, seq_num))
        if instr is not None:
            instr.producers = list(set(instr.producers) | set(producers))
        else:
            existing = self.pending_producers.get((core_id, seq_num))
            if existing is not None:
                existing.extend(p for p in producers if p not in existing)
            else:
                self.pending_producers[(core_id, seq_num)] = list(producers)

    def _merge_producers(self, core_id, seq_num, producers):
        instr = self.instructions.get((core_id, seq_num))
        if instr is not None:
            existing = set(instr.producers)
            for p in producers:
                if p not in existing:
                    instr.producers.append(p)
                    existing.add(p)
        else:
            existing = self.pending_producers.get((core_id, seq_num))
            if existing is not None:
                for p in producers:
                    if p not in existing:
                        existing.append(p)
            else:
                self.pending_producers[(core_id, seq_num)] = list(producers)

    def parse_line(self, line: str):
        is_usview = line.startswith(self.USCOPE_PREFIX)
        if is_usview:
            rest = line[len(self.USCOPE_PREFIX) :]
        elif line.startswith(self.PREFIX):
            rest = line[len(self.PREFIX) :]
        else:
            return

        if is_usview:
            if rest.startswith("deps:"):
                core_id, seq_num, producers = self._parse_deps_line(rest[5:])
                self._apply_producers(core_id, seq_num, producers)
                return
            if rest.startswith("memdeps:"):
                core_id, seq_num, producers = self._parse_deps_line(rest[8:])
                self._merge_producers(core_id, seq_num, producers)
                return
            if rest.startswith("usinfo:"):
                result = self._parse_usinfo_line(rest[7:])
                if result is not None:
                    us_core_id, us_seq_num, us_opclass = result
                    if self.current_instr is not None and self.current_seq_num == us_seq_num:
                        self.current_instr.core_id = us_core_id
                        self.current_instr.opclass = us_opclass
                return
            return

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

            if (core_id, seq_num) in self.pending_producers:
                self.current_instr.producers = self.pending_producers.pop((core_id, seq_num))
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
