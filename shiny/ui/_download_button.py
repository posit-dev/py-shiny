__all__ = ("download_button", "download_link")

from typing import Optional

from htmltools import Tag, TagAttrValue, TagChild, css, tags

from .._docstring import add_example
from .._shinyenv import is_pyodide
from ..module import resolve_id


@add_example()
def download_button(
    id: str,
    label: TagChild,
    *,
    icon: TagChild = None,
    width: Optional[str] = None,
    **kwargs: TagAttrValue,
) -> Tag:
    """
    Create a download button

    Parameters
    ----------
    id
        An id for the download.
    label
        An input label.
    icon
        An icon to display on the button.
    width
        The width of the button.
    **kwargs
        Additional attributes for the button.

    Returns
    -------
    :
        A UI element

    See Also
    --------
    * :class:`~shiny.render.download`
    * :func:`~shiny.ui.download_link`
    """

    return tags.a(
        icon,
        label,
        {
            "class": "btn btn-default shiny-download-link disabled",
            "style": css(width=width),
        },
        id=resolve_id(id),
        href="",
        target="_blank",
        # We can't use `download` in pyodide mode, because the browser chooses not to
        # route the download through the service worker in that case. (Observed by
        # jcheng on 1/7/2022, using Chrome Version 96.0.4664.110.)
        download=None if is_pyodide else True,
        aria_disabled="true",
        tabindex="-1",
        **kwargs,
    )


@add_example()
def download_link(
    id: str,
    label: TagChild,
    *,
    icon: TagChild = None,
    width: Optional[str] = None,
    **kwargs: TagAttrValue,
) -> Tag:
    """
    Create a download button.

    Parameters
    ----------
    id
        An id for the download.
    label
        An input label.
    icon
        An icon to display on the button.
    width
        The width of the button.
    **kwargs
        Additional attributes for the button.

    Returns
    -------
    :
        A UI element

    See Also
    --------
    * :class:`~shiny.render.download`
    * :func:`~shiny.ui.download_button`
    """

    return tags.a(
        icon,
        label,
        {"class": "shiny-download-link disabled", "style": css(width=width)},
        id=resolve_id(id),
        href="",
        target="_blank",
        download=None if is_pyodide else True,
        aria_disabled="true",
        tabindex="-1",
        **kwargs,
    )
