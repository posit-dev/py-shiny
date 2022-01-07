from htmltools import tags, Tag, TagChildArg, TagAttrArg, css
from typing import Optional
from .shinyenv import is_pyodide


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
        # We can't use `download` in pyodide mode, because the browser chooses not to
        # route the download through the service worker in that case. (Observed by
        # jcheng on 1/7/2022, using Chrome Version 96.0.4664.110.)
        download=None if is_pyodide else True,
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
        download=None if is_pyodide else True,
        **kwargs,
    )
