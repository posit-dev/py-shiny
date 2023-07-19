from __future__ import annotations

import json
from typing import Literal, Optional

from htmltools import Tag, TagAttrs, TagAttrValue, TagChild, TagList, div

from ... import Session
from ..._utils import drop_none
from ...session import require_active_session

# from ._color import get_color_contrast
from ._utils import consolidate_attrs
from ._web_component import web_component


def tooltip(
    trigger: TagChild,
    *args: TagChild | TagAttrs,
    id: Optional[str] = None,
    placement: Literal["auto", "top", "right", "bottom", "left"] = "auto",
    options: Optional[dict[str, object]] = None,
    **kwargs: TagAttrValue,
) -> Tag:
    """
    Add a tooltip to a UI element

    Display additional information when focusing (or hovering over) a UI element.

    Parameters
    ----------
    trigger
        A UI element (i.e., :class:`~htmltools.Tag`) to serve as the tooltips trigger.
        It's good practice for this element to be a keyboard-focusable and interactive
        element (e.g., :func:`~shiny.ui.input_action_button`,
        :func:`~shiny.ui.input_action_link`, etc.) so that the tooltip is accessible to
        keyboard and assistive technology users.
    *args
        Contents to the tooltip's body. Or tag attributes that are supplied to the
        resolved :class:`~htmltools.Tag` object.
    id
        A character string. Required to re-actively respond to the visibility of the
        tooltip (via the `input[id]` value) and/or update the visibility/contents of the
        tooltip.
    placement
        The placement of the tooltip relative to its trigger.
    options
        A list of additional [Bootstrap
        options](https://getbootstrap.com/docs/5.2/components/tooltips/#options).

    Details
    -------

    If `trigger` yields multiple HTML elements (e.g., a :class:`~htmltools.TagList` or
    complex [`shinywidgets`](https://github.com/rstudio/py-shinywidgets) object), the
    last HTML element is used as the trigger. If the `trigger` should contain all of
    those elements, wrap the object in a :func:`~htmltools.div` or :func:`~htmltools.span`.

    See Also
    --------

    * [Bootstrap tooltips documentation](https://getbootstrap.com/docs/5.2/components/tooltips/)
    """
    attrs, children = consolidate_attrs(*args, **kwargs)

    if len(children) == 0:
        raise RuntimeError("At least one value must be provided to `*args: TagChild`")

    res = web_component(
        "bslib-tooltip",
        {
            "id": id,
            "placement": placement,
            "options": json.dumps(options) if options else None,
        },
        attrs,
        # Use display:none instead of <template> since shiny.js
        # doesn't bind to the contents of the latter
        div(*children, {"style": "display:none;"}),
        trigger,
    )

    return res


def _session_on_flush_send_msg(
    id: str, session: Session | None, msg: dict[str, object]
) -> None:
    session = require_active_session(session)
    session.on_flush(lambda: session.send_input_message(id, msg), once=True)


def tooltip_toggle(
    id: str, show: Optional[bool] = None, session: Optional[Session] = None
) -> None:
    """
    Programmatically show/hide a tooltip

    Parameters
    ----------
    id
        A character string that matches an existing tooltip id.
    show
        Whether to show (`True`) or hide (`False`) the tooltip. The default (`None`)
        will show if currently hidden and hide if currently shown. Note that a tooltip
        will not be shown if the trigger is not visible (e.g., it's hidden behind a
        tab).
    session
        A Shiny session object (the default should almost always be used).
    """
    _session_on_flush_send_msg(
        id,
        session,
        {
            "method": "toggle",
            "value": _normalize_show_value(show),
        },
    )


# @describeIn tooltip Update the contents of a tooltip.
# @export
def update_tooltip(id: str, *args: TagChild, session: Optional[Session] = None) -> None:
    _session_on_flush_send_msg(
        id,
        session,
        drop_none(
            {
                "method": "update",
                "title": require_active_session(session)._process_ui(TagList(*args))
                if len(args) > 0
                else None,
            }
        ),
    )


def _normalize_show_value(show: bool | None) -> Literal["toggle", "show", "hide"]:
    if show is None:
        return "toggle"
    return "show" if show else "hide"
