from __future__ import annotations

import json
from typing import Literal, Optional

from htmltools import Tag, TagAttrs, TagAttrValue, TagChild, tags

from .._docstring import add_example
from .._namespaces import resolve_id_or_none
from ._tag import consolidate_attrs
from ._web_component import web_component


@add_example()
def tooltip(
    trigger: TagChild,
    *args: TagChild | TagAttrs,
    id: Optional[str] = None,
    placement: Literal["auto", "top", "right", "bottom", "left"] = "auto",
    options: Optional[dict[str, object]] = None,
    **kwargs: TagAttrValue,
) -> Tag:
    """
    Add a tooltip to a UI element.

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
        A character string. Required to reactively respond to the visibility of the
        tooltip (via the `input[id]` value) and/or update the visibility/contents of the
        tooltip.
    placement
        The placement of the tooltip relative to its trigger.
    options
        A list of additional [Bootstrap
        options](https://getbootstrap.com/docs/5.3/components/tooltips/#options).

    Details
    -------

    If `trigger` yields multiple HTML elements (e.g., a :class:`~htmltools.TagList` or
    complex [`shinywidgets`](https://github.com/posit-dev/py-shinywidgets) object), the
    last HTML element is used as the trigger. If the `trigger` should contain all of
    those elements, wrap the object in a :func:`~shiny.ui.tags.div` or
    :func:`~shiny.ui.tags.span`.

    Accessibility of Tooltip Triggers
    ---------------------------------

    Because the user needs to interact with the `trigger` element to see the `tooltip`,
    it's best practice to use an element that is typically accessible via keyboard
    interactions, like a button or a link.

    If you use a non-interactive element, like a `<span>` or text, `tooltip()` will
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
    icon_title = "About tooltips"
    def bs_info_icon(title: str):
        # Enhanced from https://rstudio.github.io/bsicons/ via `bsicons::bs_icon("info-circle", title = icon_title)`
        return ui.HTML(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" class="bi bi-info-circle " style="height:1em;width:1em;fill:currentColor;" aria-hidden="true" role="img" ><title>{title}</title><path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"></path><path d="m8.93 6.588-2.29.287-.082.38.45.083c.294.07.352.176.288.469l-.738 3.468c-.194.897.105 1.319.808 1.319.545 0 1.178-.252 1.465-.598l.088-.416c-.2.176-.492.246-.686.246-.275 0-.375-.193-.304-.533L8.93 6.588zM9 4.5a1 1 0 1 1-2 0 1 1 0 0 1 2 0z"></path></svg>')

    ui.tooltip(
        bs_info_icon(icon_title),
        "Text shown in the tooltip."
    )
    ```

    ```python
    icon_title = "About tooltips"
    def fa_info_circle(title: str):
        # Enhanced from https://rstudio.github.io/fontawesome/ via `fontawesome::fa("info-circle", a11y = "sem", title = icon_title)`
        return ui.HTML(f'<svg aria-hidden="true" role="img" viewBox="0 0 512 512" style="height:1em;width:1em;vertical-align:-0.125em;margin-left:auto;margin-right:auto;font-size:inherit;fill:currentColor;overflow:visible;position:relative;"><title>{title}</title><path d="M256 512A256 256 0 1 0 256 0a256 256 0 1 0 0 512zM216 336h24V272H216c-13.3 0-24-10.7-24-24s10.7-24 24-24h48c13.3 0 24 10.7 24 24v88h8c13.3 0 24 10.7 24 24s-10.7 24-24 24H216c-13.3 0-24-10.7-24-24s10.7-24 24-24zm40-208a32 32 0 1 1 0 64 32 32 0 1 1 0-64z"/></svg>')
    ui.tooltip(
        fa_info_circle(icon_title),
        "Text shown in the tooltip."
    )
    ```

    See Also
    --------

    * [Bootstrap tooltips documentation](https://getbootstrap.com/docs/5.3/components/tooltips/)
    """

    # * If you're using [bsicons::bs_icon()], provide a `title`.
    # * If you're using [fontawesome::fa()], set `a11y = "sem"` and provide a `title`.

    # Theming/Styling
    # ---------------
    #
    # Like other bslib components, tooltips can be themed by supplying [relevant theming
    # variables](https://rstudio.github.io/bslib/articles/bs5-variables.html#tooltip-bg)
    # to [bs_theme()], which effects styling of every tooltip on the page. To style a
    # _specific_ tooltip differently from other tooltips, utilize the `customClass`
    # option:
    #
    # ```
    # tooltip(
    #     "Trigger", "Tooltip message",
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
