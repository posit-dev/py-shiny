from __future__ import annotations

import json
from typing import Any, Literal, Optional

from htmltools import Tag, TagAttrs, TagAttrValue, TagChild, TagList, div, tags

from ..._namespaces import resolve_id_or_none
from ..._utils import drop_none
from ...session import Session, require_active_session
from ._tooltip import _normalize_show_value, _session_on_flush_send_msg
from ._utils import consolidate_attrs
from ._web_component import web_component

__all__ = (
    "popover",
    "toggle_popover",
    "update_popover",
)


def popover(
    trigger: TagChild,
    *args: TagChild | TagAttrs,
    title: Optional[TagChild] = None,
    id: Optional[str] = None,
    placement: Literal["auto", "top", "right", "bottom", "left"] = "auto",
    options: Optional[dict[str, Any]] = None,
    **kwargs: TagAttrValue,
) -> Tag:
    """
    Add a popover to a UI element.

    Display additional information when clicking on a UI element (typically a
    button).

    Parameters
    ----------
    trigger
        The UI element to serve as the popover trigger (typically a
        :func:`~shiny.ui.input_action_button` or similar). If `trigger` renders as
        multiple HTML elements (e.g., it's a :func:`~shiny.ui.tags.TagList`), the last
        HTML element is used for the trigger. If the `trigger` should contain all of
        those elements, wrap the object in a :func:`~shiny.ui.tags.div` or
        :func:`~shiny.ui.tags.span`.
    *args
        UI elements for the popover's body. Character strings are
        automatically escaped unless marked as :func:`~shiny.html`.
    title
        A title (header) for the popover.
    id
        A character string. Required to re-actively respond to the visibility of the
        popover (via the `input.<ID>()` value) and/or update the visibility/contents of
        the popover.
    placement
        The placement of the popover relative to its trigger.
    options
        A list of additional
        `options <https://getbootstrap.com/docs/5.3/components/popovers/#options>`_.


    Closing popovers
    ----------------

    In addition to clicking the `close_button`, popovers can be closed by pressing the
    Esc/Space key when the popover (and/or its trigger) is focused.

    See Also
    --------
    * <https://getbootstrap.com/docs/5.3/components/popovers/>
    * :func:`~shiny.experimental.ui.toggle_popover`
    * :func:`~shiny.experimental.ui.update_popover`
    * :func:`~shiny.experimental.ui.tooltip`
    """

    # Theming/Styling
    # ---------------
    #
    # Like other bslib components, popovers can be themed by supplying [relevant theming
    # variables](https://rstudio.github.io/bslib/articles/bs5-variables.html#popover-bg)
    # to [bs_theme()], which effects styling of every popover on the page. To style a
    # _specific_ popover differently from other popovers, utilize the `customClass`
    # option:
    #
    # ```
    # popover(
    #     "Trigger", "Popover message",
    #     options = list(customClass = "my-pop")
    # )
    # ```
    #
    # And then add relevant rules to [bs_theme()] via [bs_add_rules()]:
    #
    # ```
    # bs_theme() |> bs_add_rules(".my-pop { max-width: none; }")
    # ```

    attrs, children = consolidate_attrs(*args, **kwargs)
    if len(children) == 0:
        raise RuntimeError("At least one value must be provided to `popover(*args)`.")

    if options:
        for name in ("content", "title", "placement"):
            if name in options:
                raise RuntimeError(
                    f"The key `{name}` in `popover(options=)` cannot be specified directly."
                )

    res = web_component(
        "bslib-popover",
        # Use display:none instead of <template> since shiny.js
        # doesn't bind to the contents of the latter
        tags.template(
            div(*children, style="display:contents;"),
            div(title, style="display:contents;"),
        ),
        trigger,
        id=resolve_id_or_none(id),
        placement=placement,
        bsOptions=json.dumps(drop_none(options or {})),
        **attrs,
    )

    return res


def toggle_popover(
    id: str,
    show: Optional[bool] = None,
    session: Optional[Session] = None,
) -> None:
    """
    Programmatically show/hide a popover.

    Parameters
    ----------
    id
        The id of the popover DOM element to update.
    show
        Whether to show (`True`) or hide (`False`) the popover. The default
        (`None`) will show if currently hidden and hide if currently shown.
        Note that a popover will not be shown if the trigger is not visible
        (e.g., it is hidden behind a tab).
    session
        A Shiny session object (the default should almost always be used).

    See Also
    --------
    * :func:`~shiny.experimental.ui.popover`
    * :func:`~shiny.experimental.ui.update_popover`
    """
    session = require_active_session(session)

    _session_on_flush_send_msg(
        id,
        session,
        {
            "method": "toggle",
            "value": _normalize_show_value(show),
        },
    )


def update_popover(
    id: str,
    *args: TagChild,
    title: Optional[TagChild] = None,
    session: Optional[Session] = None,
) -> None:
    """
    Update the contents or title of a popover.

    Parameters
    ----------
    id
        The id of the popover DOM element to update.
    args
        The new contents of the popover.
    title
        The new title of the popover.
    session
        A Shiny session object (the default should almost always be used).

    See Also
    --------
    * :func:`~shiny.experimental.ui.popover`
    * :func:`~shiny.experimental.ui.toggle_popover`
    """
    session = require_active_session(session)

    _session_on_flush_send_msg(
        id,
        session,
        drop_none(
            {
                "method": "update",
                "content": session._process_ui(TagList(*args))
                if len(args) > 0
                else None,
                "header": session._process_ui(title) if title is not None else None,
            },
        ),
    )
