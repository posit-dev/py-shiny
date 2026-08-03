from __future__ import annotations

from collections import defaultdict
from typing import Any, Iterator

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


def _iter_rendered_links(
    contents: list[Any] | None, location: str
) -> Iterator[tuple[str, str]]:
    """
    Yield `(name, location)` for every link a `contents` list renders.

    `kind: page` groups render a link of their own and are then walked, because a
    duplicate nested inside a group renders twice just like one at section level.
    """
    for content in contents or []:
        name = _quartodoc_content_name(content)
        yield name, location

        nested = content.get("contents") if isinstance(content, dict) else None
        if nested:
            yield from _iter_rendered_links(nested, f"{location} > page {name!r}")


def test_quartodoc_configs_have_unique_contents():
    error_messages: list[str] = []

    for config_path in QUARTODOC_CONFIGS:
        for section in load_quartodoc_sections(config_path):
            section_location = f"section {section.get('title')!r}"
            locations: dict[str, list[str]] = defaultdict(list)

            for name, location in _iter_rendered_links(
                section.get("contents"), section_location
            ):
                locations[name].append(location)

            duplicates = {
                name: where for name, where in locations.items() if len(where) > 1
            }

            if duplicates:
                duplicate_list = "\n".join(
                    sorted(
                        f"  - {name} rendered {len(where)} times"
                        f" (in {', '.join(dict.fromkeys(where))})"
                        for name, where in duplicates.items()
                    )
                )
                error_messages.append(
                    f"Duplicate contents in {config_path}:\n{duplicate_list}"
                )

    if error_messages:
        pytest.fail("\n\n".join(error_messages), pytrace=False)

    assert QUARTODOC_CONFIGS, "No Quartodoc configs were found."
