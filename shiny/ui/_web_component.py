from __future__ import annotations

from htmltools import Tag, TagAttrs, TagAttrValue, TagChild

from ._html_deps_shinyverse import components_dependencies


def web_component(
    tag_name: str,
    *args: TagChild | TagAttrs,
    **kwargs: TagAttrValue,
) -> Tag:
    return Tag(
        tag_name,
        components_dependencies(),
        *args,
        _add_ws=False,
        **kwargs,
    )
