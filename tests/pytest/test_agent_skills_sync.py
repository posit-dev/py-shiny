"""Guard that bundled Agent Skills stay in sync with the public APIs they document.

The bundled `shiny-for-python` skill (``shiny/.agents/skills/``) is user-facing
documentation, with one per-topic reference file under ``references/``, but
nothing at runtime fails if the code a reference describes is renamed or removed
-- the reference just silently goes stale. These tests assert that the API
surface a reference documents is still mentioned in its file, so renames and
removals fail loudly here. They check presence only, not prose accuracy.
"""

from __future__ import annotations

from pathlib import Path

import shiny.otel
from shiny.otel._collect import OtelCollectLevel

REPO_ROOT = Path(__file__).parents[2]
REFERENCES_DIR = (
    REPO_ROOT / "shiny" / ".agents" / "skills" / "shiny-for-python" / "references"
)


def reference_text(topic: str) -> str:
    return (REFERENCES_DIR / f"{topic}.md").read_text()


def test_otel_reference_mentions_public_exports() -> None:
    text = reference_text("otel")
    for export in shiny.otel.__all__:
        assert f"otel.{export}" in text, (
            f"shiny.otel.__all__ export `{export}` is not mentioned in the otel "
            "reference -- update references/otel.md to match the public API."
        )


def test_otel_reference_mentions_collect_levels() -> None:
    text = reference_text("otel")
    assert "SHINY_OTEL_COLLECT" in text
    for level in OtelCollectLevel:
        assert f"`{level.name.lower()}`" in text, (
            f"OtelCollectLevel.{level.name} is not documented in the otel "
            "reference's collection-levels table."
        )
