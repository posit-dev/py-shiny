from click.testing import CliRunner

from shiny._main import main
from shiny._main._quickstart import QUICKSTART_TEXT


def test_quickstart_outputs_markdown() -> None:
    result = CliRunner().invoke(main, ["quickstart"])

    assert result.exit_code == 0
    assert result.output == QUICKSTART_TEXT
    assert "# Shiny for Python Quickstart" in result.output
    assert "from shiny.express import input, render, ui" in result.output
    assert "shiny run --reload app.py" in result.output
    assert "shiny docs" in result.output
    assert "uvx library-skills" in result.output


def test_quickstart_fits_standard_terminal_height() -> None:
    result = CliRunner().invoke(main, ["quickstart"])

    assert result.exit_code == 0
    lines = result.output.splitlines()
    assert 20 <= len(lines) <= 45
