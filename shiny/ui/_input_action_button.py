__all__ = ("input_action_button", "input_action_link")

from typing import Optional

from htmltools import tags, Tag, TagChildArg, TagAttrArg, css

from .._docstring import doc

__all__ = (
    "input_action_button",
    "input_action_link",
)

_topics = {
    "Server value": """
A :class:`~shiny.types.ActionButtonValue`. This class differs from
ordinary integers in that a value of 0 is considered "falsy". This implies two
things:

* :func:`~shiny.event` won't execute on initial load (by default).
* Input validation (e.g., :func:`~shiny.req`) will fail on initial load.
"""
}


@doc(
    """
    Creates an action button whose value is initially zero, and increments by one each
    time it is pressed.
    """,
    parameters={"kwargs": "Attributes to be applied to the button."},
    returns="A UI element",
    topics=_topics,
    see_also=[
        ":func:`~shiny.event`",
        ":func:`~shiny.ui.input_action_link`",
        ":func:`~shiny.reactive.effect`",
    ],
)
def input_action_button(
    id: str,
    label: TagChildArg,
    icon: TagChildArg = None,
    width: Optional[str] = None,
    **kwargs: TagAttrArg,
) -> Tag:
    return tags.button(
        {"class": "btn btn-default action-button", "style": css(width=width)},
        icon,
        label,
        id=id,
        type="button",
        **kwargs,
    )


@doc(
    """
    Creates a link whose value is initially zero, and increments by one each time it is
    pressed.
    """,
    parameters={"kwargs": "Attributes to be applied to the link."},
    returns="A UI element",
    topics=_topics,
    see_also=[
        ":func:`~shiny.event`",
        ":func:`~shiny.ui.input_action_button`",
    ],
)
def input_action_link(
    id: str,
    label: TagChildArg,
    icon: TagChildArg = None,
    **kwargs: TagAttrArg,
) -> Tag:
    return tags.a({"class": "action-button"}, icon, label, id=id, href="#", **kwargs)
