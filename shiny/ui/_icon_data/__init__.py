from __future__ import annotations

# Icon data files bundled with Shiny:
#
# fa_icons.json  — Font Awesome Free 6.x (1,852 icons)
#   Source: https://github.com/FortAwesome/Font-Awesome (icons.json from the free set)
#   This file is identical in structure to the one distributed by the `faicons` package.
#   To update: download icons.json from a Font Awesome release and replace this file.
#   Only the free tier icons are included (solid, regular, brands styles).
#
# bs_icons.json  — Bootstrap Icons 1.x (2,078 icons)
#   Source: https://github.com/twbs/icons
#   To update: run `scripts/update_bs_icons.py` (or manually fetch the SVG files
#   from the Bootstrap Icons release and regenerate the JSON using the same schema).
#
# Both files are lazily loaded on first use and cached for the process lifetime.

import json
from pathlib import Path
from typing import Any

_bs_icons: dict[str, Any] | None = None
_fa_icons: dict[str, Any] | None = None


def _load_bs_icons() -> dict[str, Any]:
    global _bs_icons
    if _bs_icons is None:
        icons_path = Path(__file__).parent / "bs_icons.json"
        with open(icons_path, encoding="utf-8") as f:
            _bs_icons = json.load(f)
    return _bs_icons


def _load_fa_icons() -> dict[str, Any]:
    global _fa_icons
    if _fa_icons is None:
        icons_path = Path(__file__).parent / "fa_icons.json"
        with open(icons_path, encoding="utf-8") as f:
            _fa_icons = json.load(f)
    return _fa_icons


def __getattr__(name: str) -> Any:
    if name == "BS_ICONS":
        return _load_bs_icons()
    if name == "FA_ICONS":
        return _load_fa_icons()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ("BS_ICONS", "FA_ICONS")
