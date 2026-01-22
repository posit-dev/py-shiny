"""Tests for shiny._main_generate_test helpers."""

from __future__ import annotations

import os
import types
from pathlib import Path

import click
import pytest

from shiny._main_generate_test import (
    ValidationError,
    create_file_validator,
    generate_test_file,
    get_app_file_path,
    get_output_file_path,
    validate_api_key,
)


def test_create_file_validator() -> None:
    validator = create_file_validator("test", must_exist=False)
    assert validator("/tmp/file.txt") is True

    validator2 = create_file_validator("app", must_exist=True)
    assert "not found" in str(validator2("/tmp/missing.txt"))

    validator3 = create_file_validator("test", must_exist=False, prefix_required="test_")
    assert "must start" in str(validator3("foo.py"))


def test_validate_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ValidationError, match="OPENAI_API_KEY"):
        validate_api_key("openai")

    monkeypatch.setenv("OPENAI_API_KEY", "x")
    validate_api_key("openai")

    with pytest.raises(ValidationError, match="Unsupported provider"):
        validate_api_key("nope")


def test_get_app_file_path_nonexistent(tmp_path: Path) -> None:
    with pytest.raises(ValidationError, match="does not exist"):
        get_app_file_path(str(tmp_path / "missing.py"))


def test_get_app_file_path_interactive_cancel(monkeypatch: pytest.MonkeyPatch) -> None:
    class DummyQuestion:
        def ask(self):
            return None

    monkeypatch.setattr("questionary.path", lambda *args, **kwargs: DummyQuestion())

    with pytest.raises(SystemExit):
        get_app_file_path(None)


def test_get_output_file_path_validations(tmp_path: Path) -> None:
    app_path = tmp_path / "app.py"
    app_path.write_text("print('x')")

    existing = tmp_path / "test_app.py"
    existing.write_text("x")

    with pytest.raises(ValidationError, match="already exists"):
        get_output_file_path(str(existing), app_path)

    with pytest.raises(ValidationError, match="must start"):
        get_output_file_path(str(tmp_path / "bad.py"), app_path)

    out = get_output_file_path(str(tmp_path / "test_new.py"), app_path)
    assert out.name == "test_new.py"


def test_generate_test_file_success(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    app_file = tmp_path / "app.py"
    app_file.write_text("print('x')")
    output_file = tmp_path / "test_app.py"

    class DummyGen:
        def __init__(self, provider: str, setup_logging: bool = False):
            self.provider = provider

        def generate_test_from_file(self, app_file_path: str, model: str | None, output_file: str):
            Path(output_file).write_text("# test")
            return None, Path(output_file)

    fake_module = types.SimpleNamespace(ShinyTestGenerator=DummyGen)
    monkeypatch.setitem(
        __import__("sys").modules,
        "shiny.pytest._generate",
        fake_module,
    )

    messages: list[str] = []

    def fake_echo(msg: str = "") -> None:
        messages.append(str(msg))

    monkeypatch.setattr(click, "echo", fake_echo)
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    monkeypatch.setattr(Path, "cwd", classmethod(lambda cls: tmp_path))

    generate_test_file(
        app_file=str(app_file),
        output_file=str(output_file),
        provider="openai",
        model="gpt-5",
    )

    assert output_file.exists()
    assert any("Test file generated" in m for m in messages)


def test_generate_test_file_validation_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("shiny._main_generate_test.validate_api_key", lambda _: (_ for _ in ()).throw(ValidationError("bad")))

    with pytest.raises(SystemExit):
        generate_test_file(
            app_file=None,
            output_file=None,
            provider="openai",
            model=None,
        )
