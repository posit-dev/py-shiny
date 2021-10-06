from typing import Optional
from htmltools import tags, tag, css, TagChild, TagAttr

# TODO: implement icon
def input_button(
    id: str,
    label: str,
    *args: TagChild,
    width: Optional[str] = None,
    **kwargs: TagAttr,
) -> tag:
    return tags.button(
        label,
        *args,
        id=id,
        type="button",
        class_="btn btn-default action-button",
        style=css(width=width),
        **kwargs,
    )


def input_link(id: str, label: str, *args: TagChild, **kwargs: TagAttr) -> tag:
    return tags.a(label, *args, id=id, href="#", class_="action-button", **kwargs)
