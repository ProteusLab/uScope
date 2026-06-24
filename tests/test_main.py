import pytest
import sys
import json
import logging
from pathlib import Path

from uScope.main import main


def test_main_basic(tmp_path: Path, monkeypatch):
    input_file = tmp_path.joinpath("trace.out")

    content = """\
O3PipeView:fetch:1000:0x1000:0:1:add x1, x2, x3:IntAlu
O3PipeView:decode:1100
O3PipeView:rename:1150
O3PipeView:dispatch:1200
O3PipeView:issue:1300
O3PipeView:complete:1400
O3PipeView:retire:1500:store:0
"""

    input_file.write_text(content)
    output_file = tmp_path.joinpath("output.json")

    monkeypatch.setattr(
        sys,
        "argv",
        ["uscope", "--input-file", str(input_file), "--output-file", str(output_file)],
    )
    main()

    assert output_file.exists()
    data = json.loads(output_file.read_text())
    assert isinstance(data, list)


def test_main_verbose(tmp_path: Path, monkeypatch, caplog):
    input_file = tmp_path.joinpath("trace.out")
    input_file.write_text(
        "O3PipeView:fetch:1000:0x1000:0:1:add x1, x2, x3:IntAlu\n"
        "O3PipeView:decode:1100\n"
        "O3PipeView:rename:1150\n"
        "O3PipeView:dispatch:1200\n"
        "O3PipeView:issue:1300\n"
        "O3PipeView:complete:1400\n"
        "O3PipeView:retire:1500:store:0\n"
    )
    output_file = tmp_path.joinpath("output.json")

    caplog.set_level(logging.DEBUG)
    monkeypatch.setattr(
        sys, "argv",
        ["uscope", "-v", "--input-file", str(input_file), "--output-file", str(output_file)],
    )
    main()
    assert output_file.exists()


def test_main_quiet(tmp_path: Path, monkeypatch, caplog):
    input_file = tmp_path.joinpath("trace.out")
    input_file.write_text(
        "O3PipeView:fetch:1000:0x1000:0:1:add x1, x2, x3:IntAlu\n"
        "O3PipeView:decode:1100\n"
        "O3PipeView:rename:1150\n"
        "O3PipeView:dispatch:1200\n"
        "O3PipeView:issue:1300\n"
        "O3PipeView:complete:1400\n"
        "O3PipeView:retire:1500:store:0\n"
    )
    output_file = tmp_path.joinpath("output.json")

    monkeypatch.setattr(
        sys, "argv",
        ["uscope", "-q", "--input-file", str(input_file), "--output-file", str(output_file)],
    )
    main()
    assert output_file.exists()


def test_main_gzip(tmp_path: Path, monkeypatch):
    input_file = tmp_path.joinpath("trace.out")
    input_file.write_text(
        "O3PipeView:fetch:1000:0x1000:0:1:add x1, x2, x3:IntAlu\n"
        "O3PipeView:decode:1100\n"
        "O3PipeView:rename:1150\n"
        "O3PipeView:dispatch:1200\n"
        "O3PipeView:issue:1300\n"
        "O3PipeView:complete:1400\n"
        "O3PipeView:retire:1500:store:0\n"
    )
    output_file = tmp_path.joinpath("output.json.gz")

    monkeypatch.setattr(
        sys, "argv",
        ["uscope", "-q", "-z", "--input-file", str(input_file), "--output-file", str(output_file)],
    )
    main()
    assert output_file.exists()
    import gzip
    data = json.loads(gzip.open(output_file, 'rt').read())
    assert isinstance(data, list)


def test_main_empty_trace(tmp_path: Path, monkeypatch):
    input_file = tmp_path.joinpath("trace.out")
    input_file.write_text("")
    output_file = tmp_path.joinpath("output.json")

    monkeypatch.setattr(
        sys, "argv",
        ["uscope", "-q", "--input-file", str(input_file), "--output-file", str(output_file)],
    )
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 1


def test_main_file_not_found(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(
        sys, "argv",
        ["uscope", "-q", "--input-file", str(tmp_path / "nonexistent.out"), "--output-file", str(tmp_path / "out.json")],
    )
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 2


def test_main_non_out_extension(tmp_path: Path, monkeypatch):
    input_file = tmp_path.joinpath("trace.txt")
    input_file.write_text(
        "O3PipeView:fetch:1000:0x1000:0:1:add x1, x2, x3:IntAlu\n"
        "O3PipeView:decode:1100\n"
        "O3PipeView:rename:1150\n"
        "O3PipeView:dispatch:1200\n"
        "O3PipeView:issue:1300\n"
        "O3PipeView:complete:1400\n"
        "O3PipeView:retire:1500:store:0\n"
    )
    output_file = tmp_path.joinpath("output.json")

    monkeypatch.setattr(
        sys, "argv",
        ["uscope", "-q", "--input-file", str(input_file), "--output-file", str(output_file)],
    )
    main()
    assert output_file.exists()


def test_main_auto_output_name(tmp_path: Path, monkeypatch):
    input_file = tmp_path.joinpath("trace.out")
    input_file.write_text(
        "O3PipeView:fetch:1000:0x1000:0:1:add x1, x2, x3:IntAlu\n"
        "O3PipeView:decode:1100\n"
        "O3PipeView:rename:1150\n"
        "O3PipeView:dispatch:1200\n"
        "O3PipeView:issue:1300\n"
        "O3PipeView:complete:1400\n"
        "O3PipeView:retire:1500:store:0\n"
    )
    expected_output = tmp_path.joinpath("trace.json")

    monkeypatch.setattr(
        sys, "argv",
        ["uscope", "-q", "--input-file", str(input_file)],
    )
    main()
    assert expected_output.exists()


def test_main_gzip_auto_extension(tmp_path: Path, monkeypatch):
    input_file = tmp_path.joinpath("trace.out")
    input_file.write_text(
        "O3PipeView:fetch:1000:0x1000:0:1:add x1, x2, x3:IntAlu\n"
        "O3PipeView:decode:1100\n"
        "O3PipeView:rename:1150\n"
        "O3PipeView:dispatch:1200\n"
        "O3PipeView:issue:1300\n"
        "O3PipeView:complete:1400\n"
        "O3PipeView:retire:1500:store:0\n"
    )
    expected_output = tmp_path.joinpath("trace.json.gz")

    monkeypatch.setattr(
        sys, "argv",
        ["uscope", "-q", "-z", "--input-file", str(input_file)],
    )
    main()
    assert expected_output.exists()
    import gzip
    data = json.loads(gzip.open(expected_output, 'rt').read())
    assert isinstance(data, list)


def test_main_auto_output_txt_extension(tmp_path: Path, monkeypatch):
    input_file = tmp_path.joinpath("trace.txt")
    input_file.write_text(
        "O3PipeView:fetch:1000:0x1000:0:1:add x1, x2, x3:IntAlu\n"
        "O3PipeView:decode:1100\n"
        "O3PipeView:rename:1150\n"
        "O3PipeView:dispatch:1200\n"
        "O3PipeView:issue:1300\n"
        "O3PipeView:complete:1400\n"
        "O3PipeView:retire:1500:store:0\n"
    )
    expected_output = tmp_path.joinpath("trace.txt.json")

    monkeypatch.setattr(
        sys, "argv",
        ["uscope", "-q", "--input-file", str(input_file)],
    )
    main()
    assert expected_output.exists()
