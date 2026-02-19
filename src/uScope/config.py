import json
from pathlib import Path
from typing import Any, Optional

class Config:
    def __init__(self, data: dict):
        self._data = data
        for key, value in data.items():
            if isinstance(value, dict):
                setattr(self, key, Config(value))
            else:
                setattr(self, key, value)

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
