import json
from pathlib import Path
from typing import Any, Optional
from abc import ABC, abstractmethod

from .O3 import PipelineStage, OpClass, Instruction
from .utils import stable_hash

class IConfig(ABC):
    @abstractmethod
    def get_func_unit(self, opclass: OpClass) -> str:
        assert False, f"Functional Unit getter method wasn't defined in {type(self).__name__}"

    @abstractmethod
    def get_stage_name(self, stage : PipelineStage) -> str:
        assert False, f"Pipeline stage name mapping method wasn't defined in {type(self).__name__}"

    @abstractmethod
    def get_color_for_instr(self, instr : Instruction) -> str:
        assert False, f"Color mapping method wasn't defined in {type(self).__name__}"

    @abstractmethod
    def pipeline_pid(self) -> int:
        assert False, f"Pipeline Process ID wasn't defined in {type(self).__name__}"

    @abstractmethod
    def func_units_pid(self) -> int:
        assert False, f"Functional Units Process ID wasn't wasn't defined in {type(self).__name__}"

    @abstractmethod
    def pipeline_width(self) -> int:
        assert False, f"Pipeline width wasn't defined in {type(self).__name__}"

    @abstractmethod
    def func_units_width(self) -> int:
        assert False, f"Functional Units width wasn't defined in {type(self).__name__}"

class Config(IConfig):
    def __init__(self, data: dict):
        self._data = data
        for key, value in data.items():
            if isinstance(value, dict):
                setattr(self, f"_{key}", Config(value))
            else:
                setattr(self, f"_{key}", value)

    @property
    def settings(self):
        return self._settings

    @property
    def pipeline_pid(self) -> int:
        return self.settings._PID_PIPELINE_STAGES_BASE

    @property
    def func_units_pid(self) -> int:
        return self.settings._PID_FUNC_UNITS_BASE

    @property
    def pipeline_width(self) -> int:
        return self.settings._MAX_PIPE_WIDTH

    @property
    def func_units_width(self) -> int:
        return self.settings._MAX_FUNC_UNITS_WIDTH

    def get_func_unit(self, opclass: Any) -> str:
        return self._func_units.get(str(opclass), "No_OpClass")

    def get_stage_name(self, stage : PipelineStage) -> str:
        return self._stage_names[stage.value]

    def get_color_for_func_unit(self, unit) -> str:
        return self._colors.get(unit, self._colors._default)

    def get_color_for_instr(self, instr : Instruction) -> str:
        unit = self.get_func_unit(instr.opclass)
        family = self._colors.get(unit, self._colors._default)
        idx = stable_hash(instr.mnemonic, len(family))
        return family[idx]

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __contains__(self, key: str) -> bool:
        return key in self._data

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def as_dict(self) -> dict:
        return self._data.copy()


def load_config(config_path: Optional[Path] = None) -> Config:
    config_data = {}

    builtin_dir = Path(__file__).parent.joinpath("configs")

    if builtin_dir.is_dir():
        for json_file in builtin_dir.glob("*.json"):
            key = json_file.stem
            with open(json_file, 'r', encoding='utf-8') as f:
                config_data[key] = json.load(f)

    if config_path is not None and config_path.is_dir():
        for json_file in config_path.glob("*.json"):
            key = json_file.stem
            with open(json_file, 'r', encoding='utf-8') as f:
                config_data[key] = json.load(f)

    return Config(config_data)
