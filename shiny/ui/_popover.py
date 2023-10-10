from __future__ import annotations

import json
from typing import Any, Literal, Optional

from htmltools import Tag, TagAttrs, TagAttrValue, TagChild, div, tags

from .._namespaces import resolve_id_or_none
from .._utils import drop_none
from ._web_component import web_component
from ._x._utils import consolidate_attrs


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
        `options <https://getbootstrap.com/docs/5.2/components/popovers/#options>`_.


    Closing popovers
    ----------------

    In addition to clicking the `close_button`, popovers can be closed by pressing the
    Esc/Space key when the popover (and/or its trigger) is focused.

    See Also
    --------
    * <https://getbootstrap.com/docs/5.2/components/popovers/>
    * :func:`~shiny.ui.toggle_popover`
    * :func:`~shiny.ui.update_popover`
    * :func:`~shiny.ui.tooltip`
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
