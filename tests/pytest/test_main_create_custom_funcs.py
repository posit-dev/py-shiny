"""Tests for shiny._main_create_custom helpers."""

from __future__ import annotations

from pathlib import Path

import pytest
from prompt_toolkit.document import Document
from questionary import ValidationError

from shiny._main_create_custom import (
    ComponentNameValidator,
    is_existing_module,
    is_pep508_identifier,
    update_component_name_in_template,
)


def test_is_existing_module(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_find_spec(name: str):
        if name == "exists":
            return object()
        return None

    monkeypatch.setattr("shiny._main_create_custom.util.find_spec", fake_find_spec)
    assert is_existing_module("exists") is True
    assert is_existing_module("missing") is False

    def fake_find_spec_error(name: str):
        raise ImportError("boom")

    monkeypatch.setattr("shiny._main_create_custom.util.find_spec", fake_find_spec_error)
    assert is_existing_module("anything") is False


def test_is_pep508_identifier() -> None:
    assert is_pep508_identifier("valid-name") is True
    assert is_pep508_identifier("Invalid") is True
    assert is_pep508_identifier("bad name") is False


def test_component_name_validator_rejects_cases(monkeypatch: pytest.MonkeyPatch) -> None:
    validator = ComponentNameValidator()

    with pytest.raises(ValidationError):
        validator.validate(Document(""))

    with pytest.raises(ValidationError):
        validator.validate(Document("has_underscore"))

    with pytest.raises(ValidationError):
        validator.validate(Document("HasUpper"))

    with pytest.raises(ValidationError):
        validator.validate(Document("'quoted'"))

    with pytest.raises(ValidationError):
        validator.validate(Document("x" * 215))

    with pytest.raises(ValidationError):
        validator.validate(Document("bad name"))

    monkeypatch.setattr("shiny._main_create_custom.is_existing_module", lambda _: True)
    with pytest.raises(ValidationError):
        validator.validate(Document("existing"))


def test_component_name_validator_accepts(monkeypatch: pytest.MonkeyPatch) -> None:
    validator = ComponentNameValidator()
    monkeypatch.setattr("shiny._main_create_custom.is_existing_module", lambda _: False)
    validator.validate(Document("good-name"))


def test_update_component_name_in_template(tmp_path: Path) -> None:
    template_dir = tmp_path
    (template_dir / "custom_component").mkdir()
    (template_dir / "custom_component" / "custom_component.py").write_text(
        "custom_component custom-component CustomComponent"
    )
    (template_dir / "srcts").mkdir()
    (template_dir / "srcts" / "file.txt").write_text(
        "custom_component custom-component CustomComponent"
    )
    (template_dir / "example-app").mkdir()
    (template_dir / "example-app" / "readme.md").write_text(
        "custom_component custom-component CustomComponent"
    )

    update_component_name_in_template(template_dir, "new component")

    new_pkg = template_dir / "new_component"
    assert new_pkg.is_dir()
    assert (new_pkg / "new_component.py").exists()

    for path in [
        new_pkg / "new_component.py",
        template_dir / "srcts" / "file.txt",
        template_dir / "example-app" / "readme.md",
    ]:
        content = path.read_text()
        assert "new_component" in content
        assert "new-component" in content
        assert "NewComponent" in content
