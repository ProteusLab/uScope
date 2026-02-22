import pytest, json
from pathlib import Path

from uScope.O3 import PipelineStage, OpClass
from uScope.config import Config, load_config


def test_colors(minimal_parser, config: Config):
    instr = list(minimal_parser.instructions.values())[0]
    cname = config.get_color_for_instr(instr)

    possible_colors = config.get_color_for_func_unit("IntALU")
    assert cname in possible_colors


def test_config_dict_methods(config: Config):
    assert "settings" in config
    assert "SomethingUndefinedClass" not in config
    assert config.get("settings") is not None
    assert config.get("SomethingUndefinedClass", "default") == "default"
    assert isinstance(config.as_dict(), dict)


def test_config_load_from_custom_dir(tmp_path: Path):
    config_dir = tmp_path.joinpath("config")
    config_dir.mkdir()
    stage_names = {"fetch": "MY_FETCH", "decode": "MY_DECODE"}
    (config_dir.joinpath("stage_names.json")).write_text(json.dumps(stage_names))
    config = load_config(config_dir)
    assert config.get_stage_name(PipelineStage.FETCH) == "MY_FETCH"
    assert config.get_func_unit(OpClass.IntAlu) is not None


def test_config_load_from_nonexist_dir(tmp_path: Path):
    nonexist = tmp_path.joinpath("nonexist")
    config = load_config(nonexist)
    assert config.get_stage_name(PipelineStage.FETCH) is not None
