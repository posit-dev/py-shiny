from __future__ import annotations

import inspect
from types import ModuleType
from typing import Any, Dict, List, Optional

from . import render, ui
from .render.renderer import Renderer

COMPONENT_CATEGORIES = (
    "layout",
    "cards",
    "inputs",
    "outputs",
    "renderers",
    "other",
)


def _category_for(namespace: str, name: str) -> str:
    if namespace == "render":
        return "renderers"
    if name.startswith("input_"):
        return "inputs"
    if name.startswith(("output_", "download_")):
        return "outputs"
    if name.startswith(("card", "accordion", "value_box", "showcase_")):
        return "cards"
    if name.startswith(
        ("page_", "layout_", "nav_", "navset_", "navbar_", "panel_", "sidebar")
    ) or name in {"column", "row"}:
        return "layout"
    return "other"


def _summary(docstring: str) -> str:
    first_paragraph = docstring.split("\n\n", 1)[0]
    return " ".join(line.strip() for line in first_paragraph.splitlines())


def _is_documentable(namespace: str, obj: object) -> bool:
    if namespace == "render":
        return inspect.isclass(obj) and issubclass(obj, Renderer)
    return inspect.isfunction(obj) or inspect.isclass(obj)


def _component_entry(
    namespace: str, module: ModuleType, name: str
) -> Optional[Dict[str, Any]]:
    obj = getattr(module, name, None)
    if obj is None or not _is_documentable(namespace, obj):
        return None

    docstring = inspect.getdoc(obj) or ""
    entry: Dict[str, Any] = {
        "name": f"{namespace}.{name}",
        "category": _category_for(namespace, name),
        "description": _summary(docstring),
        "docstring": docstring,
    }
    try:
        entry["signature"] = str(inspect.signature(obj))
    except (TypeError, ValueError):
        pass
    return entry


def _discover_components() -> List[Dict[str, Any]]:
    components: List[Dict[str, Any]] = []
    for namespace, module in (("ui", ui), ("render", render)):
        for name in module.__all__:
            entry = _component_entry(namespace, module, name)
            if entry is not None:
                components.append(entry)
    return sorted(components, key=lambda item: (item["category"], item["name"]))


def list_components(category: Optional[str] = None) -> List[Dict[str, Any]]:
    components = _discover_components()
    if category is None:
        return components
    return [item for item in components if item["category"] == category]


def get_component_doc(name: str) -> Optional[Dict[str, Any]]:
    if name.startswith(("ui.", "render.")):
        lookup_names = (name,)
    else:
        lookup_names = (f"ui.{name}", f"render.{name}")

    components = {item["name"]: item for item in _discover_components()}
    for lookup_name in lookup_names:
        if lookup_name in components:
            return components[lookup_name]
    return None
