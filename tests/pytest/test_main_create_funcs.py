"""Tests for shiny._main_create helpers."""

from __future__ import annotations

import io
import json
import zipfile
from pathlib import Path
from typing import Any

import click
import pytest

from shiny._main_create import (
    ShinyInternalTemplates,
    ShinyTemplate,
    choice_from_templates,
    download_and_extract_zip,
    github_zip_url,
    parse_github_arg,
    parse_github_spec,
    parse_github_url,
    template_by_name,
)


def _write_template(path: Path, payload: dict[str, Any]) -> None:
    path.mkdir(parents=True, exist_ok=True)
    (path / "_template.json").write_text(json.dumps(payload))


def test_choice_from_templates_returns_choices(tmp_path: Path) -> None:
    template = ShinyTemplate(id="t1", path=tmp_path, title="Title")
    choices = choice_from_templates([template])
    assert len(choices) == 1
    assert choices[0].value == "t1"


def test_shinytemplate_express_available_cached(tmp_path: Path) -> None:
    template = ShinyTemplate(id="t1", path=tmp_path)
    assert template.express_available is False
    (tmp_path / "app-express.py").write_text("print('x')")
    assert template.express_available is False

    fresh = ShinyTemplate(id="t2", path=tmp_path)
    assert fresh.express_available is True


def test_find_templates_invalid_json(tmp_path: Path) -> None:
    template_dir = tmp_path / "app"
    template_dir.mkdir()
    (template_dir / "_template.json").write_text("{")

    with pytest.raises(ValueError, match="Error parsing"):
        from shiny import _main_create

        _main_create.find_templates(tmp_path)


def test_find_templates_missing_id(tmp_path: Path) -> None:
    _write_template(tmp_path / "app", {"title": "No id"})

    with pytest.raises(ValueError, match="missing a 'id'"):
        from shiny import _main_create

        _main_create.find_templates(tmp_path)


def test_find_templates_duplicate_ids_warns(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _write_template(tmp_path / "app1", {"id": "dup"})
    _write_template(tmp_path / "app2", {"id": "dup"})

    messages: list[str] = []

    def fake_echo(msg: str) -> None:
        messages.append(str(msg))

    monkeypatch.setattr(click, "echo", fake_echo)

    from shiny import _main_create

    templates = _main_create.find_templates(tmp_path)
    assert len(templates) == 2
    assert any("duplicate IDs" in msg for msg in messages)


def test_template_by_name_returns_template(tmp_path: Path) -> None:
    template = ShinyTemplate(id="t1", path=tmp_path)
    assert template_by_name([template], "t1") is template
    assert template_by_name([template], "missing") is None


def test_internal_templates_cache(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []

    def fake_find_templates(path: Path) -> list[ShinyTemplate]:
        calls.append(str(path))
        return [ShinyTemplate(id="t1", path=path)]

    from shiny import _main_create

    monkeypatch.setattr(_main_create, "find_templates", fake_find_templates)

    templates = ShinyInternalTemplates()
    _ = templates.apps
    _ = templates.apps
    assert len(calls) == 1


def test_parse_github_spec_variants() -> None:
    spec = parse_github_spec("owner/repo@main:subdir")
    assert spec.repo_owner == "owner"
    assert spec.repo_name == "repo"
    assert spec.ref == "main"
    assert spec.path == "subdir"

    spec2 = parse_github_spec("owner/repo:subdir@dev")
    assert spec2.ref == "dev"
    assert spec2.path == "subdir"

    spec3 = parse_github_spec("owner/repo/path/to/template")
    assert spec3.ref == "HEAD"
    assert spec3.path == "path/to/template"


def test_parse_github_url_and_arg() -> None:
    url = "https://github.com/owner/repo/tree/main/templates/app"
    parsed = parse_github_url(url)
    assert parsed.repo_owner == "owner"
    assert parsed.repo_name == "repo"
    assert parsed.ref == "main"
    assert parsed.path == "templates/app"

    parsed_arg = parse_github_arg(url)
    assert parsed_arg.repo_owner == "owner"


def test_github_zip_url_order() -> None:
    spec = parse_github_spec("owner/repo@v1")
    urls = list(github_zip_url(spec))
    assert urls[0].endswith("refs/heads/v1.zip")
    assert urls[1].endswith("refs/tags/v1.zip")
    assert urls[2].endswith("/v1.zip")


def test_download_and_extract_zip_single_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    in_memory = io.BytesIO()
    with zipfile.ZipFile(in_memory, "w") as zf:
        zf.writestr("repo-root/file.txt", "data")

    data = in_memory.getvalue()

    class DummyResponse:
        def read(self) -> bytes:
            return data

    monkeypatch.setattr("shiny._main_create.urlopen", lambda url: DummyResponse())

    extracted = download_and_extract_zip("https://example.com/repo.zip", tmp_path)
    assert extracted.name == "repo-root"
    assert (extracted / "file.txt").exists()
