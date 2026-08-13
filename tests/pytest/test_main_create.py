from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from click.testing import CliRunner

from shiny._main import _create, main


@pytest.fixture
def captured_templates(monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    """Record calls to the template helpers so no prompts or downloads happen."""
    captured: dict[str, Any] = {}

    def fake_internal(*args: Any, **kwargs: Any) -> None:
        captured["internal"] = (args, kwargs)

    def fake_github(*args: Any, **kwargs: Any) -> None:
        captured["github"] = (args, kwargs)

    monkeypatch.setattr(_create, "use_internal_template", fake_internal)
    monkeypatch.setattr(_create, "use_github_template", fake_github)
    return captured


def test_create_uses_internal_template(captured_templates: dict[str, Any]) -> None:
    result = CliRunner().invoke(
        main,
        ["create", "--template", "basic-app", "--mode", "core", "--dir", "my-dir"],
    )

    assert result.exit_code == 0
    assert "github" not in captured_templates
    args, _ = captured_templates["internal"]
    assert args == ("basic-app", "core", Path("my-dir"), None)


def test_create_uses_github_template(captured_templates: dict[str, Any]) -> None:
    result = CliRunner().invoke(
        main,
        [
            "create",
            "--github",
            "posit-dev/py-shiny-templates:dashboard",
            "--dir",
            "my-dir",
            "--package-name",
            "mypkg",
        ],
    )

    assert result.exit_code == 0
    assert "internal" not in captured_templates
    args, kwargs = captured_templates["github"]
    assert args == ("posit-dev/py-shiny-templates:dashboard",)
    assert kwargs == {
        "template_name": None,
        "mode": None,
        "dest_dir": Path("my-dir"),
        "package_name": "mypkg",
    }


def test_create_rejects_invalid_mode(captured_templates: dict[str, Any]) -> None:
    result = CliRunner().invoke(main, ["create", "--mode", "bogus"])

    assert result.exit_code != 0
    assert captured_templates == {}


def test_internal_templates_are_discovered() -> None:
    # Guards the __file__-relative lookup of shiny/templates/
    assert len(_create.shiny_internal_templates.apps) > 0
    assert len(_create.shiny_internal_templates.packages) > 0
