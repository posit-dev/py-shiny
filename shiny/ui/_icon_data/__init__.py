from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_bs_icons: dict[str, Any] | None = None


def _load_bs_icons() -> dict[str, Any]:
    global _bs_icons
    if _bs_icons is None:
        icons_path = Path(__file__).parent / "bs_icons.json"
        with open(icons_path, encoding="utf-8") as f:
            _bs_icons = json.load(f)
    return _bs_icons


def __getattr__(name: str) -> Any:
    if name == "BS_ICONS":
        return _load_bs_icons()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ("BS_ICONS",)
