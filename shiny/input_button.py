from htmltools import tags, Tag, TagChildArg, TagAttrArg, css
from typing import Optional


# TODO: implement icon
def input_button(
    id: str,
    label: str,
    *args: TagChildArg,
    width: Optional[str] = None,
    **kwargs: TagAttrArg,
) -> Tag:
    return tags.button(
        label,
        *args,
        id=id,
        type="button",
        class_="btn btn-default action-button",
        style=css(width=width),
        **kwargs,
    )


def input_link(id: str, label: str, *args: TagChildArg, **kwargs: TagAttrArg) -> Tag:
    return tags.a(label, *args, id=id, href="#", class_="action-button", **kwargs)
