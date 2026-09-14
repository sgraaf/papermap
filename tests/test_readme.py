"""Tests that the usage examples in README.md run.

Rendering and saving are stubbed out, so that the examples are checked without
downloading any tiles.
"""

import re
import shlex
from pathlib import Path

import pytest
from click.testing import CliRunner

from papermap.cli import cli
from papermap.papermap import PaperMap

README_PATH = Path(__file__).parent.parent / "README.md"

CODE_BLOCK_PATTERN = re.compile(
    r"^```(?P<language>python|shell)\n(?P<code>.*?)^```", re.DOTALL | re.MULTILINE
)

GPX = """\
<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="papermap-test" xmlns="http://www.topografix.com/GPX/1/1">
  <trk><name>Hike</name><trkseg>
    <trkpt lat="46.5197" lon="7.9577"/>
    <trkpt lat="46.5250" lon="7.9650"/>
  </trkseg></trk>
</gpx>
"""


def readme_code_blocks(language: str) -> dict[str, str]:
    """Return the code blocks of the given language in the README, keyed by their line number."""
    readme = README_PATH.read_text(encoding="utf-8")
    return {
        f"line-{readme[: match.start()].count(chr(10)) + 1}": match["code"]
        for match in CODE_BLOCK_PATTERN.finditer(readme)
        if match["language"] == language
    }


PYTHON_CODE_BLOCKS = readme_code_blocks("python")
SHELL_CODE_BLOCKS = readme_code_blocks("shell")


@pytest.fixture(autouse=True)
def _stub_render_and_save(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Stub out rendering and saving, and run in a directory with a GPX file."""
    monkeypatch.setattr(PaperMap, "render", lambda _self: None)
    monkeypatch.setattr(PaperMap, "save", lambda _self, _file: None)
    monkeypatch.chdir(tmp_path)
    (tmp_path / "hike.gpx").write_text(GPX, encoding="utf-8")


@pytest.mark.parametrize(
    "code", PYTHON_CODE_BLOCKS.values(), ids=PYTHON_CODE_BLOCKS.keys()
)
def test_python_example(code: str) -> None:
    source = "\n".join(
        line.removeprefix(">>>").removeprefix("...").removeprefix(" ")
        for line in code.splitlines()
    )
    exec(source, {})  # noqa: S102


@pytest.mark.parametrize(
    "code", SHELL_CODE_BLOCKS.values(), ids=SHELL_CODE_BLOCKS.keys()
)
def test_shell_example(code: str) -> None:
    command = shlex.split(code.replace("\\\n", " ").removeprefix("$ "))
    assert command[0] == "papermap"
    result = CliRunner().invoke(cli, command[1:])
    assert result.exit_code == 0, result.output
