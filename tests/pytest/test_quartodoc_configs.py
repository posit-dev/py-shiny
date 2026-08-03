from __future__ import annotations

import pytest
import yaml

from ._quartodoc_utils import QUARTODOC_CONFIGS, load_quartodoc_sections


def _quartodoc_content_name(content: object) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, dict):
        name = content.get("name") or content.get("path")
        if isinstance(name, str):
            return name
        return yaml.safe_dump(content, sort_keys=True)
    return repr(content)


def test_quartodoc_configs_have_unique_contents():
    error_messages: list[str] = []

    for config_path in QUARTODOC_CONFIGS:
        for section in load_quartodoc_sections(config_path):
            seen: set[str] = set()
            duplicates: list[str] = []

            for content in section.get("contents", []):
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
