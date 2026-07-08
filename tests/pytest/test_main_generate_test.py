from __future__ import annotations

from typing import Any

import pytest
from click.testing import CliRunner

from shiny._main import _generate_test, main


@pytest.fixture
def captured_generate(monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    """Record calls to generate_test_file so no AI provider is contacted."""
    captured: dict[str, Any] = {}

    def fake_generate_test_file(**kwargs: Any) -> None:
        captured.update(kwargs)

    monkeypatch.setattr(_generate_test, "generate_test_file", fake_generate_test_file)
    return captured


def test_add_group_lists_test_command() -> None:
    result = CliRunner().invoke(main, ["add", "--help"])

    assert result.exit_code == 0
    assert "test" in result.output


def test_add_test_forwards_options(captured_generate: dict[str, Any]) -> None:
    result = CliRunner().invoke(
        main,
        [
            "add",
            "test",
            "--app",
            "myapp.py",
            "--test-file",
            "test_myapp.py",
            "--provider",
            "openai",
            "--model",
            "gpt-5",
        ],
    )

    assert result.exit_code == 0
    assert captured_generate == {
        "app_file": "myapp.py",
        "output_file": "test_myapp.py",
        "provider": "openai",
        "model": "gpt-5",
    }


def test_add_test_defaults(captured_generate: dict[str, Any]) -> None:
    result = CliRunner().invoke(main, ["add", "test"])

    assert result.exit_code == 0
    assert captured_generate == {
        "app_file": None,
        "output_file": None,
        "provider": "anthropic",
        "model": None,
    }


def test_add_test_rejects_unknown_provider(captured_generate: dict[str, Any]) -> None:
    result = CliRunner().invoke(main, ["add", "test", "--provider", "bogus"])

    assert result.exit_code != 0
    assert captured_generate == {}
