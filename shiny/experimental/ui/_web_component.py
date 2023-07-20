from __future__ import annotations

from htmltools import Tag, TagAttrs, TagAttrValue, TagChild

from ._htmldeps import web_component_dependency


def web_component(
    tag_name: str,
    *args: TagChild | TagAttrs,
    **kwargs: TagAttrValue,
) -> Tag:
    return Tag(
        tag_name,
        web_component_dependency(),
        *args,
        _add_ws=False,
        **kwargs,
    )
