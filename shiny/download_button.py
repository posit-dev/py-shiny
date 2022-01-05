from htmltools import tags, Tag, TagChildArg, TagAttrArg, css
from typing import Optional


# TODO: implement icon
def download_button(
    id: str,
    label: str,
    *args: TagChildArg,
    class_: Optional[str] = None,
    width: Optional[str] = None,
    **kwargs: TagAttrArg,
) -> Tag:
    return tags.a(
        label,
        *args,
        id=id,
        class_=f"btn btn-default shiny-download-link {class_}",
        style=css(width=width),
        href="",
        target="_blank",
        download=True,
        **kwargs,
    )


def download_link(
    id: str,
    label: str,
    *args: TagChildArg,
    class_: Optional[str] = None,
    width: Optional[str] = None,
    **kwargs: TagAttrArg,
) -> Tag:
    return tags.a(
        label,
        *args,
        id=id,
        class_=f"shiny-download-link {class_}",
        style=css(width=width),
        href="",
        target="_blank",
        download=True,
        **kwargs,
    )
