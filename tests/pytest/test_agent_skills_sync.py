"""Guard that bundled Agent Skills stay in sync with the public APIs they document.

Bundled skills (``shiny/.agents/skills/``) are user-facing documentation, but
nothing at runtime fails if the code they describe is renamed or removed -- the
skill just silently goes stale. These tests assert that the API surface a skill
documents is still mentioned in its ``SKILL.md``, so renames and removals fail
loudly here. They check presence only, not prose accuracy.
"""

from __future__ import annotations

from pathlib import Path

import shiny.otel
from shiny.otel._collect import OtelCollectLevel

REPO_ROOT = Path(__file__).parents[2]
SKILLS_DIR = REPO_ROOT / "shiny" / ".agents" / "skills"


def skill_md_text(name: str) -> str:
    return (SKILLS_DIR / name / "SKILL.md").read_text()


def test_otel_skill_mentions_public_exports() -> None:
    text = skill_md_text("otel")
    for export in shiny.otel.__all__:
        assert f"otel.{export}" in text, (
            f"shiny.otel.__all__ export `{export}` is not mentioned in the otel "
            "SKILL.md -- update the skill to match the public API."
        )


def test_otel_skill_mentions_collect_levels() -> None:
    text = skill_md_text("otel")
    assert "SHINY_OTEL_COLLECT" in text
    for level in OtelCollectLevel:
        assert f"`{level.name.lower()}`" in text, (
            f"OtelCollectLevel.{level.name} is not documented in the otel "
            "SKILL.md's collection-levels table."
        )
