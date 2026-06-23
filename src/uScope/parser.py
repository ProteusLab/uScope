from tqdm import tqdm

from .O3 import Instruction, PipelineStage


def _count_lines(filename: str) -> int:
    count = 0
    with open(filename, "rb") as f:
        for _ in f:
            count += 1
    return count


class PipeViewParser:
    PREFIX = "O3PipeView:"

    def __init__(self):
        self.instructions = {}
        self.current_seq_num = None
        self.current_instr = None
        self.stage_map = {f"{stage}": stage for stage in PipelineStage.order()}

    def parse_file(self, filename: str, progress: bool = True):
        total = _count_lines(filename)
        pbar = tqdm(
            total=total,
            desc="Parsing trace",
            unit="lines",
            disable=not progress,
            leave=False,
        )

        with open(filename, "r") as f:
            for line in f:
                pbar.update(1)
                line = line.strip()
                if line:
                    self.parse_line(line)

        pbar.close()

        if self.current_instr is not None:
            self.instructions[self.current_seq_num] = self.current_instr

        self.instructions = {
            seq: instr
            for seq, instr in self.instructions.items()
            if sum(1 for tick in instr.stages.values() if tick > 0) > 0
        }

    @staticmethod
    def _parse_fetch_line(rest: str):
        parts = rest.split(":", 5)
        if len(parts) != 6:
            return None
        tick_str, pc, _, seq_str, disasm, opclass = parts
        return int(tick_str), pc, int(seq_str), disasm.strip(), opclass.strip()

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
            tick, pc, seq_num, disasm, opclass = result

            if self.current_instr is not None:
                self.instructions[self.current_seq_num] = self.current_instr

            self.current_seq_num = seq_num
            self.current_instr = Instruction(
                seq_num=seq_num,
                pc=pc,
                disasm=disasm,
                opclass=opclass,
                stages={},
                stage_order=[],
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

            if stage_name == "retire" and store_tick > 0:
                self.current_instr.store_tick = store_tick
