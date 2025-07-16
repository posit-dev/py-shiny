from __future__ import annotations

import json
from typing import Any, Literal, Optional

from htmltools import Tag, TagAttrs, TagAttrValue, TagChild, div, tags

from .._docstring import add_example
from .._namespaces import resolve_id_or_none
from .._utils import drop_none
from ._tag import consolidate_attrs
from ._web_component import web_component


@add_example()
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
        multiple HTML elements (e.g., it's a :class:`~shiny.ui.TagList`), the last
        HTML element is used for the trigger. If the `trigger` should contain all of
        those elements, wrap the object in a :func:`~shiny.ui.tags.div` or
        :func:`~shiny.ui.tags.span`.
    *args
        UI elements for the popover's body. Character strings are
        automatically escaped unless marked as :class:`~shiny.ui.HTML`.
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

    Accessibility of Popover Triggers
    ---------------------------------

    Because the user needs to interact with the `trigger` element to see the `popover`,
    it's best practice to use an element that is typically accessible via keyboard
    interactions, like a button or a link.

    If you use a non-interactive element, like a `<span>` or text, `popover()` will
    automatically add the `tabindex="0"` attribute to the trigger element to make sure
    that users can reach the element with the keyboard. This means that in most cases
    you can use any element you want as the trigger.

    One place where it's important to consider the accessibility of the trigger is when
    using an icon without any accompanying text. In these cases, many icon elements are
    created with the assumption that the icon is decorative, which will make it
    inaccessible to users of assistive technologies.

    When using an icon as the primary trigger, ensure that the icon does not have
    `aria-hidden="true"` or `role="presentation"` attributes. Icon packages typically
    provide a way to specify a title for the icon, as well as a way to specify that the
    icon is not decorative. The title should be a short description of the purpose of
    the trigger, rather than a description of the icon itself.

    For example:

    ```python
    icon_title = "Settings"
    def bs_gear_icon(title: str):
        # Enhanced from https://rstudio.github.io/bsicons/ via `bsicons::bs_icon("gear", title = icon_title)`
        return ui.HTML(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" class="bi bi-gear " style="height:1em;width:1em;fill:currentColor;" aria-hidden="true" role="img" ><title>{title}</title><path d="M8 4.754a3.246 3.246 0 1 0 0 6.492 3.246 3.246 0 0 0 0-6.492zM5.754 8a2.246 2.246 0 1 1 4.492 0 2.246 2.246 0 0 1-4.492 0z"></path><path d="M9.796 1.343c-.527-1.79-3.065-1.79-3.592 0l-.094.319a.873.873 0 0 1-1.255.52l-.292-.16c-1.64-.892-3.433.902-2.54 2.541l.159.292a.873.873 0 0 1-.52 1.255l-.319.094c-1.79.527-1.79 3.065 0 3.592l.319.094a.873.873 0 0 1 .52 1.255l-.16.292c-.892 1.64.901 3.434 2.541 2.54l.292-.159a.873.873 0 0 1 1.255.52l.094.319c.527 1.79 3.065 1.79 3.592 0l.094-.319a.873.873 0 0 1 1.255-.52l.292.16c1.64.893 3.434-.902 2.54-2.541l-.159-.292a.873.873 0 0 1 .52-1.255l.319-.094c1.79-.527 1.79-3.065 0-3.592l-.319-.094a.873.873 0 0 1-.52-1.255l.16-.292c.893-1.64-.902-3.433-2.541-2.54l-.292.159a.873.873 0 0 1-1.255-.52l-.094-.319zm-2.633.283c.246-.835 1.428-.835 1.674 0l.094.319a1.873 1.873 0 0 0 2.693 1.115l.291-.16c.764-.415 1.6.42 1.184 1.185l-.159.292a1.873 1.873 0 0 0 1.116 2.692l.318.094c.835.246.835 1.428 0 1.674l-.319.094a1.873 1.873 0 0 0-1.115 2.693l.16.291c.415.764-.42 1.6-1.185 1.184l-.291-.159a1.873 1.873 0 0 0-2.693 1.116l-.094.318c-.246.835-1.428.835-1.674 0l-.094-.319a1.873 1.873 0 0 0-2.692-1.115l-.292.16c-.764.415-1.6-.42-1.184-1.185l.159-.291A1.873 1.873 0 0 0 1.945 8.93l-.319-.094c-.835-.246-.835-1.428 0-1.674l.319-.094A1.873 1.873 0 0 0 3.06 4.377l-.16-.292c-.415-.764.42-1.6 1.185-1.184l.292.159a1.873 1.873 0 0 0 2.692-1.115l.094-.319z"></path></svg>')

    ui.popover(
        bs_gear_icon(icon_title),
        title = icon_title,
        ui.input_slider("n", "Number of points", 1, 100, 50)
    )
    ```

    ```python
    icon_title = "Settings"
    def fa_gear_icon(title: str):
        # Enhanced from https://rstudio.github.io/fontawesome/ via `fontawesome::fa("gear", a11y = "sem", title = icon_title)`
        return ui.HTML(f'<svg aria-label="{title}" role="img" viewBox="0 0 512 512" style="height:1em;width:1em;vertical-align:-0.125em;margin-left:auto;margin-right:auto;font-size:inherit;fill:currentColor;overflow:visible;position:relative;"><title>{title}</title><path d="M495.9 166.6c3.2 8.7 .5 18.4-6.4 24.6l-43.3 39.4c1.1 8.3 1.7 16.8 1.7 25.4s-.6 17.1-1.7 25.4l43.3 39.4c6.9 6.2 9.6 15.9 6.4 24.6c-4.4 11.9-9.7 23.3-15.8 34.3l-4.7 8.1c-6.6 11-14 21.4-22.1 31.2c-5.9 7.2-15.7 9.6-24.5 6.8l-55.7-17.7c-13.4 10.3-28.2 18.9-44 25.4l-12.5 57.1c-2 9.1-9 16.3-18.2 17.8c-13.8 2.3-28 3.5-42.5 3.5s-28.7-1.2-42.5-3.5c-9.2-1.5-16.2-8.7-18.2-17.8l-12.5-57.1c-15.8-6.5-30.6-15.1-44-25.4L83.1 425.9c-8.8 2.8-18.6 .3-24.5-6.8c-8.1-9.8-15.5-20.2-22.1-31.2l-4.7-8.1c-6.1-11-11.4-22.4-15.8-34.3c-3.2-8.7-.5-18.4 6.4-24.6l43.3-39.4C64.6 273.1 64 264.6 64 256s.6-17.1 1.7-25.4L22.4 191.2c-6.9-6.2-9.6-15.9-6.4-24.6c4.4-11.9 9.7-23.3 15.8-34.3l4.7-8.1c6.6-11 14-21.4 22.1-31.2c5.9-7.2 15.7-9.6 24.5-6.8l55.7 17.7c13.4-10.3 28.2-18.9 44-25.4l12.5-57.1c2-9.1 9-16.3 18.2-17.8C227.3 1.2 241.5 0 256 0s28.7 1.2 42.5 3.5c9.2 1.5 16.2 8.7 18.2 17.8l12.5 57.1c15.8 6.5 30.6 15.1 44 25.4l55.7-17.7c8.8-2.8 18.6-.3 24.5 6.8c8.1 9.8 15.5 20.2 22.1 31.2l4.7 8.1c6.1 11 11.4 22.4 15.8 34.3zM256 336a80 80 0 1 0 0-160 80 80 0 1 0 0 160z"/></svg>')
    ui.popover(
        fa_gear_icon(icon_title),
        title = icon_title,
        ui.input_slider("n", "Number of points", 1, 100, 50)
    )
    ```

    See Also
    --------
    * <https://getbootstrap.com/docs/5.3/components/popovers/>
    * :func:`~shiny.ui.update_popover`
    * :func:`~shiny.ui.tooltip`
    """

    # * If you're using [bsicons::bs_icon()], provide a `title`.
    # * If you're using [fontawesome::fa()], set `a11y = "sem"` and provide a `title`.

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
    #     options = {"customClass": "my-pop"}
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
