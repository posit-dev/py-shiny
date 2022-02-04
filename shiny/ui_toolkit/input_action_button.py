from typing import Optional

from htmltools import tags, Tag, TagChildArg, TagAttrArg, css


def input_action_button(
    id: str,
    label: TagChildArg,
    icon: TagChildArg = None,
    width: Optional[str] = None,
    **kwargs: TagAttrArg,
) -> Tag:
    return tags.button(
        {"class": "btn btn-default action-button", "style": css(width=width)},
        icon,
        label,
        id=id,
        type="button",
        **kwargs,
    )


def input_action_link(
    id: str,
    label: TagChildArg,
    icon: TagChildArg = None,
    **kwargs: TagAttrArg,
) -> Tag:
    return tags.a({"class": "action-button"}, icon, label, id=id, href="#", **kwargs)
