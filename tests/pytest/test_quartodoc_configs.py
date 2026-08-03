from __future__ import annotations

from typing import Any

import pytest

from ._quartodoc_utils import QUARTODOC_CONFIGS, load_quartodoc_sections


def _quartodoc_content_name(content: str | dict[str, Any]) -> str:
    """
    Return the symbol or page name a `contents` entry renders a link for.

    A `contents` entry is either a bare symbol name or a mapping carrying a
    `name` (a symbol with options) or a `path` (a `kind: page` group).
    """
    if isinstance(content, str):
        return content
    return str(content.get("name") or content["path"])


def test_quartodoc_configs_have_unique_contents():
    error_messages: list[str] = []

    for config_path in QUARTODOC_CONFIGS:
        for section in load_quartodoc_sections(config_path):
            seen: set[str] = set()
            duplicates: list[str] = []

            for content in section.get("contents") or []:
                content_name = _quartodoc_content_name(content)
                if content_name in seen:
                    duplicates.append(content_name)
                else:
                    seen.add(content_name)

            if duplicates:
                duplicate_list = "\n".join(sorted(f"  - {x}" for x in duplicates))
                error_messages.append(
                    f"Duplicate contents in {config_path}, "
                    f"section {section.get('title')!r}:\n{duplicate_list}"
                )

    if error_messages:
        pytest.fail("\n\n".join(error_messages), pytrace=False)

    assert QUARTODOC_CONFIGS, "No Quartodoc configs were found."
