from typing import Optional

from htmltools import tags, Tag, TagChildArg, TagAttrArg, css


def input_button(
    id: str,
    label: TagChildArg,
    icon: TagChildArg = None,
    width: Optional[str] = None,
    **kwargs: TagAttrArg,
) -> Tag:
    return tags.button(
        icon,
        label,
        id=id,
        type="button",
        class_="btn btn-default action-button",
        style=css(width=width),
        **kwargs,
    )


def input_link(
    id: str,
    label: TagChildArg,
    icon: TagChildArg = None,
    **kwargs: TagAttrArg,
) -> Tag:
    return tags.a(icon, label, id=id, href="#", class_="action-button", **kwargs)
