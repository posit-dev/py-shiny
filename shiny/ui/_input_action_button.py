__all__ = ("input_action_button", "input_action_link")

from typing import Optional

from htmltools import Tag, TagAttrValue, TagChild, css, tags

from .._docstring import add_example
from ..module import resolve_id


@add_example()
@add_example("app-disabled-core.py")
def input_action_button(
    id: str,
    label: TagChild,
    *,
    icon: TagChild = None,
    width: Optional[str] = None,
    disabled: bool = False,
    **kwargs: TagAttrValue,
) -> Tag:
    """
    Creates an action button whose value is initially zero, and increments by one each
    time it is pressed.

    Parameters
    ----------
    id
        An input id.
    label
        An input label.
    icon
        An icon to appear inline with the button/link.
    width
        The CSS width, e.g. '400px', or '100%'
    disabled
        If `True`, the button will not be clickable. Use
        :func:`~shiny.ui.update_action_button` to dynamically enable/disable the button.
    **kwargs
        Attributes to be applied to the button.

    Returns
    -------
    :
        A UI element

    Notes
    ------
    ::: {.callout-note title="Server value"}
    An integer representing the number of clicks.
    :::

    See Also
    --------
    * :func:`~shiny.ui.update_action_button`
    * :func:`~shiny.ui.input_action_link`
    * :func:`~shiny.ui.input_bookmark_button`
    * :func:`~shiny.reactive.event`
    """

    if "_add_ws" not in kwargs:
        kwargs["_add_ws"] = True

    if icon is not None:
        icon = tags.span(icon, class_="action-icon")

    if label is not None:
        label = tags.span(label, class_="action-label")

    return tags.button(
        {"class": "btn btn-default action-button", "style": css(width=width)},
        icon,
        label,
        id=resolve_id(id),
        type="button",
        disabled="" if disabled else None,
        **kwargs,
    )


@add_example()
def input_action_link(
    id: str,
    label: TagChild,
    *,
    icon: TagChild = None,
    **kwargs: TagAttrValue,
) -> Tag:
    """
    Creates a link whose value is initially zero, and increments by one each time it is
    pressed.

    Parameters
    ----------
    id
        An input id.
    label
        An input label.
    icon
        An icon to appear inline with the button/link.
    **kwargs
        Attributes to be applied to the link.

    Returns
    -------
    :
        A UI element

    Notes
    ------
    ::: {.callout-note title="Server value"}
    An integer representing the number of clicks.
    :::

    See Also
    --------
    * :func:`~shiny.ui.update_action_link`
    * :func:`~shiny.ui.input_action_button`
    * :func:`~shiny.reactive.event`
    """

    if icon is not None:
        icon = tags.span(icon, class_="action-icon")

    if label is not None:
        label = tags.span(label, class_="action-label")

    return tags.a(
        {"class": "action-button action-link"},
        icon,
        label,
        id=resolve_id(id),
        href="#",
        **kwargs,
    )
