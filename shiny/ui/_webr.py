from __future__ import annotations

from htmltools import Tag, TagAttrValue

from .._namespaces import resolve_id
from ._html_deps_py_shiny import webr_dependency

__all__ = ("webr",)


def webr(
    id: str,
    **kwargs: TagAttrValue,
) -> Tag:
    id = resolve_id(id)

    return Tag("shiny-webr-component", webr_dependency(), id=id, **kwargs)
