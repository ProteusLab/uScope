import sys
import json
import pytest
from pathlib import Path
from uScope.main import main

def test_main_basic(tmp_path, monkeypatch):
    input_file = tmp_path / "trace.out"

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
    output_file = tmp_path / "output.json"
    monkeypatch.setattr(sys, 'argv', ['uscope', '--input-file', str(input_file), '--output-file', str(output_file)])
    main()
    assert output_file.exists()
    data = json.loads(output_file.read_text())
    assert isinstance(data, list)
