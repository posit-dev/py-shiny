from __future__ import annotations

from typing import Optional

from htmltools import HTML, Tag, TagAttrValue, TagChild

from .._docstring import add_example
from ..module import resolve_id
from ..types import MISSING, MISSING_TYPE
from ..ui._input_action_button import input_action_button

BOOKMARK_ID = "._bookmark_"


@add_example()
def input_bookmark_button(
    label: TagChild = "Bookmark...",
    *,
    icon: TagChild | MISSING_TYPE = MISSING,
    width: Optional[str] = None,
    disabled: bool = False,
    id: str = BOOKMARK_ID,
    title: str = "Bookmark this application's state and get a URL for sharing.",
    **kwargs: TagAttrValue,
) -> Tag:
    """
    Button for bookmarking/sharing.

    A `bookmarkButton` is a [input_action_button()] with a default label that consists of a link icon and the text "Bookmark...". It is meant to be used for bookmarking state.

    Parameters
    ----------
    label
        The button label.
    icon
        The icon to display on the button.
    width
        The CSS width, e.g. '400px', or '100%'.
    disabled
        Whether the button is disabled.
    id
        An ID for the bookmark button. The only time it is necessary to set the ID unless you have more than one bookmark button in your application. If you specify an input ID, it should be excluded from bookmarking with `session.bookmark.exclude.append(ID)`, and you must create a reactive effect that performs the bookmarking (`session.bookmark()`) when the button is pressed.
    title
        A tooltip that is shown when the mouse cursor hovers over the button.
    kwargs
        Additional attributes for the button.

    Returns
    -------
    :
        A UI element.

    See Also
    --------
    * :func:`~shiny.ui.input_action_button`
    * :func:`~shiny.ui.input_action_link`
    * :func:`~shiny.reactive.event`
    """
    resolved_id = resolve_id(id)
    if isinstance(icon, MISSING_TYPE):
        icon = HTML("&#x1F517;")

    return input_action_button(
        resolved_id,
        label,
        icon=icon,
        title=title,
        width=width,
        disabled=disabled,
        **kwargs,
    )
