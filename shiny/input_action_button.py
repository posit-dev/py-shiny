from typing import Optional

from htmltools import tags, Tag, TagChildArg, TagAttrArg, css


def input_action_button(
    id: str,
    label: TagChildArg,
    icon: TagChildArg = None,
    width: Optional[str] = None,
    **kwargs: TagAttrArg,
) -> Tag:
    kwargs["class_"] = "btn btn-default action-button " + str(kwargs.get("class_", ""))
    kwargs["style"] = css(width=width) if width else "" + str(kwargs.get("style", ""))
    return tags.button(
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
    kwargs["class_"] = "action-button " + str(kwargs.get("class_", ""))
    return tags.a(icon, label, id=id, href="#", **kwargs)
