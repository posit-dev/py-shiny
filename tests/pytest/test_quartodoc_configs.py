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
    Yield `(label, location)` for every link a `contents` list renders.

    `kind: page` groups render a link of their own and are then walked, because a
    duplicate nested inside a group renders twice just like one at section level.
    A page `path` is labelled separately from a symbol `name`: the two live in
    different namespaces, and a page deliberately named after a class it extends
    (e.g. the `Session` page) is not a duplicate of that class.
    """
    for content in contents or []:
        name = _quartodoc_content_name(content)
        nested = content.get("contents") if isinstance(content, dict) else None

        yield (f"page {name!r}" if nested else name), location

        if nested:
            yield from _iter_rendered_links(nested, f"{location} > page {name!r}")


CROSS_SECTION_ALLOWLIST: dict[str, frozenset[str]] = {
    # `shiny.express.ui` has no `download_button` / `download_link` counterpart
    # to core's `ui.download_button` / `ui.download_link`, so the Express
    # renderers are deliberately listed under both "Output components" and
    # "Uploads & downloads".
    "_quartodoc-express.yml": frozenset(
        {
            "express.render.download_button",
            "express.render.download_link",
        }
    ),
}
"""Symbols intentionally listed under more than one section, keyed by config."""


def test_quartodoc_configs_have_unique_contents():
    error_messages: list[str] = []

    for config_path in QUARTODOC_CONFIGS:
        allowed = CROSS_SECTION_ALLOWLIST.get(config_path.name, frozenset())

        # Every section of a config renders onto one API reference page, so a
        # symbol repeated across sections produces duplicate links just like one
        # repeated within a section.
        locations: dict[str, list[str]] = defaultdict(list)
        for section in load_quartodoc_sections(config_path):
            for name, location in _iter_rendered_links(
                section.get("contents"), f"section {section.get('title')!r}"
            ):
                locations[name].append(location)

        duplicates: dict[str, list[str]] = {}
        for name, where in locations.items():
            if len(where) == 1:
                continue
            # An allow-listed symbol may appear in several sections, but still
            # never twice within one section.
            if name in allowed and len(set(where)) == len(where):
                continue
            duplicates[name] = where

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
