from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

DOCS_DIR = Path(__file__).parent.parent.parent / "docs"

QUARTODOC_CONFIGS = tuple(sorted(DOCS_DIR.glob("_quartodoc-*.yml")))
"""Every Quartodoc config that drives a generated API reference page."""

QuartodocContent = str | dict[str, Any]
"""A `contents` entry: a bare symbol name, or a mapping with a `name`/`path`."""


def load_quartodoc_sections(config_path: Path) -> list[dict[str, Any]]:
    """
    Return the `quartodoc.sections` entries of a Quartodoc config file.

    Raises
    ------
    Fails the calling test if the file cannot be read (`OSError`) or is not
    valid YAML (`yaml.YAMLError`).
    """
    try:
        parsed: Any = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as e:
        pytest.fail(f"Failed to load or parse {config_path}: {e}")

    # An empty or comments-only config parses to `None`, and a key with nothing
    # under it (`sections:`) parses to `None` rather than an empty list.
    config: dict[str, Any] = parsed or {}
    quartodoc: dict[str, Any] = config.get("quartodoc") or {}
    sections: list[dict[str, Any]] = quartodoc.get("sections") or []
    return sections


def section_contents(section: dict[str, Any]) -> list[QuartodocContent]:
    """Return a section's `contents`, treating a missing or empty key as empty."""
    contents: list[QuartodocContent] = section.get("contents") or []
    return contents
