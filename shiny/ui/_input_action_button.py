__all__ = ("input_action_button", "input_action_link")

from typing import Optional

from htmltools import Tag, TagAttrValue, TagChild, css, tags

from .._docstring import add_example
from .._namespaces import resolve_id


@add_example()
def input_action_button(
    id: str,
    label: TagChild,
    *,
    icon: TagChild = None,
    width: Optional[str] = None,
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
    kwargs
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
    -------
    ~shiny.ui.input_action_link
    ~shiny.reactive.event
    """

    return tags.button(
        {"class": "btn btn-default action-button", "style": css(width=width)},
        icon,
        None if icon is None else " ",
        label,
        id=resolve_id(id),
        type="button",
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
    kwargs
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
    -------
    ~shiny.ui.input_action_button
    ~shiny.reactive.event
    """

    return tags.a(
        {"class": "action-button"},
        icon,
        label,
        id=resolve_id(id),
        href="#",
        **kwargs,
    )
