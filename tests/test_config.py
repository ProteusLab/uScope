import pytest, json

from uScope.O3 import PipelineStage, OpClass
from uScope.config import Config, load_config

def test_colors(minimal_parser, config : Config):
    instr = list(minimal_parser.instructions.values())[0]
    cname = config.get_color_for_instr(instr)

    possible_colors = config.get_color_for_func_unit("IntALU")
    assert cname in possible_colors

def test_config_dict_methods(config):
    assert "settings" in config
    assert "SomethingUndefinedClass" not in config
    assert config.get("settings") is not None
    assert config.get("SomethingUndefinedClass", "default") == "default"
    assert isinstance(config.as_dict(), dict)

def test_config_load_from_custom_dir(tmp_path):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    stage_names = {"fetch": "MY_FETCH", "decode": "MY_DECODE"}
    (config_dir / "stage_names.json").write_text(json.dumps(stage_names))
    config = load_config(config_dir)
    assert config.get_stage_name(PipelineStage.FETCH) == "MY_FETCH"
    assert config.get_func_unit(OpClass.IntAlu) is not None

def test_config_load_from_nonexist_dir(tmp_path):
    nonexist = tmp_path / "nonexist"
    config = load_config(nonexist)
    assert config.get_stage_name(PipelineStage.FETCH) is not None
