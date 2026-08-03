from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

DOCS_DIR = Path(__file__).parent.parent.parent / "docs"

QUARTODOC_CONFIGS = tuple(sorted(DOCS_DIR.glob("_quartodoc-*.yml")))
"""Every Quartodoc config that drives a generated API reference page."""


def load_quartodoc_sections(config_path: Path) -> list[dict[str, Any]]:
    """Return the `quartodoc.sections` entries of a Quartodoc config file."""
    try:
        config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    except Exception as e:
        pytest.fail(f"Failed to load or parse {config_path}: {e}")

    return config.get("quartodoc", {}).get("sections", [])
