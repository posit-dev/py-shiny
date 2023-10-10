from __future__ import annotations

import json
from typing import Literal, Optional

from htmltools import Tag, TagAttrs, TagAttrValue, TagChild, tags

from .._namespaces import resolve_id_or_none
from ._tag import consolidate_attrs
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
    complex [`shinywidgets`](https://github.com/posit-dev/py-shinywidgets) object), the
    last HTML element is used as the trigger. If the `trigger` should contain all of
    those elements, wrap the object in a :func:`~shiny.ui.tags.div` or
    :func:`~shiny.ui.tags.span`.

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
            "id": resolve_id_or_none(id),
            "placement": placement,
            "options": json.dumps(options) if options else None,
        },
        attrs,
        # Use display:none instead of <template> since shiny.js
        # doesn't bind to the contents of the latter
        tags.template(*children, {"style": "display:none;"}),
        trigger,
    )

    return res
