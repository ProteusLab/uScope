import re

from .O3 import Instruction, PipelineStage

class PipeViewParser:
    FETCH_PATTERN = re.compile(
        r'O3PipeView:fetch:(\d+):(0x[0-9a-f]+):\d+:(\d+):([^:]+):(.+)$'
    )
    STAGE_PATTERN = re.compile(
        r'O3PipeView:(\w+):(\d+)(?::.*)?$'
    )

    def __init__(self):
        self.instructions = {}
        self.current_seq_num = None
        self.current_instr = None
        self.stage_map = {
            'fetch': PipelineStage.FETCH,
            'decode': PipelineStage.DECODE,
            'rename': PipelineStage.RENAME,
            'dispatch': PipelineStage.DISPATCH,
            'issue': PipelineStage.ISSUE,
            'complete': PipelineStage.COMPLETE,
            'retire': PipelineStage.RETIRE,
        }

    def parse_file(self, filename: str):
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    self.parse_line(line)

        if self.current_instr is not None:
            self.instructions[self.current_seq_num] = self.current_instr

        self.instructions = {
            seq: instr for seq, instr in self.instructions.items()
            if sum(1 for tick in instr.stages.values() if tick > 0) > 0
        }

    def parse_line(self, line: str):
        fetch_match = self.FETCH_PATTERN.match(line)
        if fetch_match:
            if self.current_instr is not None:
                self.instructions[self.current_seq_num] = self.current_instr

            tick = int(fetch_match.group(1))
            pc = fetch_match.group(2)
            seq_num = int(fetch_match.group(3))
            disasm = fetch_match.group(4).strip()
            opclass = fetch_match.group(5).strip()

            self.current_seq_num = seq_num
            self.current_instr = Instruction(
                seq_num=seq_num,
                pc=pc,
                disasm=disasm,
                opclass=opclass,
                stages={},
                stage_order=[]
            )

            self.current_instr.stages[PipelineStage.FETCH] = tick
            self.current_instr.stage_order.append(PipelineStage.FETCH)
            return

        stage_match = self.STAGE_PATTERN.match(line)
        if stage_match and self.current_instr is not None:
            stage_name = stage_match.group(1).lower()
            tick = int(stage_match.group(2))

            if stage_name in self.stage_map:
                stage = self.stage_map[stage_name]
                self.current_instr.stages[stage] = tick

                if stage not in self.current_instr.stage_order:
                    self.current_instr.stage_order.append(stage)
