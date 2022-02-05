from typing import Optional

from htmltools import tags, Tag, TagChildArg, TagAttrArg, css

from ..shinyenv import is_pyodide


def download_button(
    id: str,
    label: TagChildArg,
    icon: TagChildArg = None,
    width: Optional[str] = None,
    **kwargs: TagAttrArg,
) -> Tag:
    return tags.a(
        icon,
        label,
        {"class": "btn btn-default shiny-download-link", "style": css(width=width)},
        id=id,
        # This is a fake link that just results in a 404. It will be replaced by a
        # working link after the server side logic runs, so this link will only be
        # visited in cases where the user clicks the button too fast, or if the server
        # never defines a handler for this download button.
        href="session/0/download/missing_download",
        target="_blank",
        # We can't use `download` in pyodide mode, because the browser chooses not to
        # route the download through the service worker in that case. (Observed by
        # jcheng on 1/7/2022, using Chrome Version 96.0.4664.110.)
        download=None if is_pyodide else True,
        **kwargs,
    )


def download_link(
    id: str,
    label: TagChildArg,
    icon: TagChildArg = None,
    width: Optional[str] = None,
    **kwargs: TagAttrArg,
) -> Tag:
    return tags.a(
        icon,
        label,
        {"class": "shiny-download-link", "style": css(width=width)},
        id=id,
        href="session/0/download/missing_download",
        target="_blank",
        download=None if is_pyodide else True,
        **kwargs,
    )
