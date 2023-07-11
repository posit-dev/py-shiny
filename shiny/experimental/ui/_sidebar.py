from __future__ import annotations

import random
from typing import Literal, Optional

from htmltools import Tag, TagAttrs, TagAttrValue, TagChild, TagList, css, div
from htmltools import svg as svgtags
from htmltools import tags

from ... import Session
from ..._deprecated import warn_deprecated
from ...session import require_active_session

# from ._color import get_color_contrast
from ._card import CardItem
from ._css_unit import CssUnit, as_css_padding, as_css_unit
from ._fill import as_fill_item, as_fillable_container
from ._htmldeps import sidebar_dependency
from ._utils import consolidate_attrs, trinary


class Sidebar:
    """
    Sidebar object

    Class returned from :func:`~shiny.experimental.ui.sidebar`. Please do not use this
    class directly. Instead, supply the :func:`~shiny.experimental.ui.sidebar` object to
    :func:`~shiny.experimental.ui.layout_sidebar`.

    Attributes
    ----------
    tag
        The :class:`~htmltools.Tag` object that represents the sidebar.
    collapse_tag
        The :class:`~htmltools.Tag` object that represents the collapse button.
    position
        Where the sidebar should appear relative to the main content.
    open
        The initial state of the sidebar.
    width
        A valid CSS unit used for the width of the sidebar.
    max_height_mobile
        The maximum height of the horizontal sidebar when viewed on mobile devices.
        The default is `250px` unless the sidebar is included in a
        :func:`~shiny.experimental.ui.layout_sidebar` with a specified height, in
        which case the default is to take up no more than 50% of the layout container.
    color_fg
        A foreground color.
    color_bg
        A background color.

    Parameters
    ----------
    tag
        The :class:`~htmltools.Tag` object that represents the sidebar.
    collapse_tag
        The :class:`~htmltools.Tag` object that represents the collapse button.
    position
        Where the sidebar should appear relative to the main content.
    open
        The initial state of the sidebar.
    width
        A valid CSS unit used for the width of the sidebar.
    max_height_mobile
        The maximum height of the horizontal sidebar when viewed on mobile devices.
        The default is `250px` unless the sidebar is included in a
        :func:`~shiny.experimental.ui.layout_sidebar` with a specified height, in
        which case the default is to take up no more than 50% of the layout container.
    color_fg
        A foreground color.
    color_bg
        A background color.


    """

    def __init__(
        self,
        tag: Tag,
        collapse_tag: Optional[Tag],
        position: Literal["left", "right"],
        open: Literal["desktop", "open", "closed", "always"],
        width: CssUnit,
        max_height_mobile: Optional[str | float],
        color_fg: Optional[str],
        color_bg: Optional[str],
    ):
        self.tag = tag
        self.collapse_tag = collapse_tag
        self.position = position
        self.open = open
        self.width = width
        self.max_height_mobile = max_height_mobile
        self.color_fg = color_fg
        self.color_bg = color_bg

    # The `Sidebar` class should use it's fields, not this method
    def tagify(self) -> Tag:
        """
        Not implemented
        """
        # Similar to `NavMenu.tagify()`
        raise NotImplementedError(
            "`Sidebar` objects must be handled by `layout_sidebar(sidebar)`."
        )


# TODO-maindocs; @add_example()
def sidebar(
    *args: TagChild | TagAttrs,
    width: CssUnit = 250,
    position: Literal["left", "right"] = "left",
    open: Literal["desktop", "open", "closed", "always"] = "desktop",
    id: Optional[str] = None,
    title: TagChild | str = None,
    bg: Optional[str] = None,
    fg: Optional[str] = None,
    class_: Optional[str] = None,  # TODO-future; Consider using `**kwargs` instead
    max_height_mobile: Optional[str | float] = None,
) -> Sidebar:
    # See [this article](https://rstudio.github.io/bslib/articles/sidebars.html)
    #   to learn more.
    # TODO-future; If color contrast is implemented. Docs for `bg` and `fg`:
    #     If only one of either is provided, an
    #     accessible contrasting color is provided for the opposite color, e.g. setting
    #     `bg` chooses an appropriate `fg` color.

    """
    Sidebar element

    Create a collapsing sidebar layout by providing a `sidebar()` object to the
    `sidebar=` argument of:

    * :func:`~shiny.experimental.ui.layout_sidebar`
      * Creates a sidebar layout component which can be dropped inside any
        :func:`~shiny.ui.page` or :func:`~shiny.experimental.ui.card` context.
    * :func:`~shiny.experimental.ui.navset_bar`, :func:`~shiny.experimental.ui.navset_tab_card`, and :func:`~shiny.experimental.ui.navset_pill_card`
      * Creates a multi page/tab UI with a singular `sidebar()` (which is
        shown on every page/tab).

    Parameters
    ----------
    *args
        Contents to the sidebar. Or tag attributes that are supplied to the
        resolved :class:`~htmltools.Tag` object.
    width
        A valid CSS unit used for the width of the sidebar.
    position
        Where the sidebar should appear relative to the main content.
    open
        The initial state of the sidebar. It can be `"desktop"` (the sidebar starts open
        on desktop screen, closed on mobile), `"open"` or `True` (the sidebar starts
        open), `"closed"` or `False` (the sidebar starts closed), or `"always"` or
        `None` (the sidebar is always open and cannot be closed).

        In :func:`~shiny.experimental.ui.sidebar_toggle`, `open` indicates the desired
        state of the sidebar, where the default of `open = None` will cause the sidebar
        to be toggled open if closed or vice versa. Note that
        :func:`~shiny.experimental.ui.sidebar_toggle` can only open or close the
        sidebar, so it does not support the `"desktop"` and `"always"` options.
    id
        A character string. Required if wanting to re-actively read (or update) the
        `collapsible` state in a Shiny app.
    title
        A character title to be used as the sidebar title, which will be wrapped in a
        `<div>` element with class `sidebar-title`. You can also provide a custom
        :func:`~shiny.htmltools.tag` for the title element, in which case you'll
        likely want to give this element `class = "sidebar-title"`.
    bg,fg
        A background or foreground color.
    class_
        CSS classes for the sidebar container element, in addition to the fixed
        `.sidebar` class.
    max_height_mobile
        The maximum height of the horizontal sidebar when viewed on mobile devices.
        The default is `250px` unless the sidebar is included in a
        :func:`~shiny.experimental.ui.layout_sidebar` with a specified height, in
        which case the default is to take up no more than 50% of the layout container.

    Returns
    -------
    :
        A :class:`~shiny.experimental.ui.Sidebar` object.

    See Also
    --------
    * :func:`~shiny.experimental.ui.layout_sidebar`
    * :func:`~shiny.experimental.ui.navset_bar`
    * :func:`~shiny.experimental.ui.navset_tab_card`
    * :func:`~shiny.experimental.ui.navset_pill_card`
    """
    # TODO-future; validate `open`, bg, fg, class_, max_height_mobile

    if id is None and open != "always":
        # but always provide id when collapsible for accessibility reasons
        id = f"bslib-sidebar-{random.randint(1000, 10000)}"

    # TODO-future; implement
    # if fg is None and bg is not None:
    #     fg = get_color_contrast(bg)
    # if bg is None and fg is not None:
    #     bg = get_color_contrast(fg)

    if isinstance(title, (str, int, float)):
        title = div(str(title), class_="sidebar-title")

    collapse_tag = None
    if open != "always":
        collapse_tag = tags.button(
            _collapse_icon(),
            class_="collapse-toggle",
            type="button",
            title="Toggle sidebar",
            aria_expanded=trinary(open in ["open", "desktop"]),
            aria_controls=id,
        )

    tag = div(
        div(
            title,
            {"class": "sidebar-content"},
            *args,
        ),
        {"class": "bslib-sidebar-input"} if id is not None else None,
        {"class": "sidebar"},
        id=id,
        role="complementary",
        class_=class_,
    )

    return Sidebar(
        tag=tag,
        collapse_tag=collapse_tag,
        position=position,
        open=open,
        width=width,
        max_height_mobile=max_height_mobile,
        color_fg=fg,
        color_bg=bg,
    )


# TODO-maindocs; @add_example()
def layout_sidebar(
    sidebar: Sidebar | TagChild | TagAttrs,
    *args: TagChild | TagAttrs,
    fillable: bool = True,
    fill: bool = True,
    bg: Optional[str] = None,
    fg: Optional[str] = None,
    border: Optional[bool] = None,
    border_radius: Optional[bool] = None,
    border_color: Optional[str] = None,
    gap: Optional[CssUnit] = None,
    padding: Optional[CssUnit | list[CssUnit]] = None,
    height: Optional[CssUnit] = None,
    **kwargs: TagAttrValue,
) -> CardItem:
    """
    Sidebar layout

    Create a sidebar layout component which can be dropped inside any
    :func:`~shiny.ui.page` or :func:`~shiny.experimental.ui.card` context.

    Parameters
    ----------
    sidebar
        A :class:`~shiny.experimental.ui.Sidebar` object created by :func:`~shiny.experimental.ui.sidebar`.
    *args
        Contents to the main content area. Or tag attributes that are supplied to the
        resolved :class:`~htmltools.Tag` object.
    fillable
        Whether or not the main content area should be wrapped in a fillable container.
        See :func:`~shiny.experimental.ui.as_fillable_container` for details.
    fill
        Whether or not the sidebar layout should be wrapped in a fillable container. See
        :func:`~shiny.experimental.ui.as_fill_item` for details.
    bg,fg
        A background or foreground color.
    border
        Whether or not to show a border around the sidebar layout.
    border_radius
        Whether or not to round the corners of the sidebar layout.
    border_color
        A border color.
    gap
        A CSS length unit defining the `gap` (i.e., spacing) between elements provided
        to `*args`. This argument is only applicable when `fillable = TRUE`.
    padding
        Padding to use for the body. This can be a numeric vector
        (which will be interpreted as pixels) or a character vector with valid CSS
        lengths. The length can be between one and four. If one, then that value
        will be used for all four sides. If two, then the first value will be used
        for the top and bottom, while the second value will be used for left and
        right. If three, then the first will be used for top, the second will be
        left and right, and the third will be bottom. If four, then the values will
        be interpreted as top, right, bottom, and left respectively.
    height
        Any valid CSS unit to use for the height.

    Returns
    -------
    :
        A :class:`~htmltools.Tag` object.

    See Also
    --------
    * :func:`~shiny.experimental.ui.sidebar`
    """
    updated_args = list(args)
    has_upgraded: bool = False
    # Use `args` here so `updated_args` can be safely altered in place
    for arg in args:
        if isinstance(arg, Sidebar):
            raise TypeError(
                "Please use the `sidebar=` argument to supply a `sidebar()`"
            )
        # TODO-future: >= 2023-11-01); Once `panel_sidebar()` is removed, we can remove this loop
        if isinstance(arg, DeprecatedPanelSidebar):
            if has_upgraded:
                raise TypeError(
                    "Multiple `panel_sidebar()` calls detected. Please use the `sidebar=` argument and supply a `sidebar()`"
                )
            if sidebar is not None:
                raise TypeError(
                    "A `panel_sidebar()` was supplied along with a `sidebar=` value. Please use only `sidebar=` to supply a `sidebar()`."
                )
            sidebar = arg.sidebar
            updated_args.remove(arg)
            has_upgraded = True

    if not isinstance(sidebar, Sidebar):
        sidebar = _sidebar_func(sidebar)

    # TODO-future; implement
    # if fg is None and bg is not None:
    #     fg = get_color_contrast(bg)
    # if bg is None and fg is not None:
    #     bg = get_color_contrast(fg)

    attrs, children = consolidate_attrs(*updated_args, **kwargs)
    # TODO-future: >= 2023-11-01); Once `panel_main()` is removed, we can remove this loop
    for child in children:
        if isinstance(child, DeprecatedPanelMain):
            attrs = consolidate_attrs(attrs, child.attrs)[0]
            # child.children will be handled when tagified

    main = div(
        {
            "role": "main",
            "class": f"main{' bslib-gap-spacing' if fillable else ''}",
            ""
            "style": css(
                background_color=bg,
                color=fg,
                gap=as_css_unit(gap),
                padding=as_css_padding(padding),
            ),
        },
        attrs,
        *children,
    )
    if fillable:
        main = as_fillable_container(main)

    max_height_mobile = sidebar.max_height_mobile or (
        "250px" if height is None else "50%"
    )

    res = div(
        {"class": "bslib-sidebar-layout"},
        {"class": "sidebar-right"} if sidebar.position == "right" else None,
        {"class": "sidebar-collapsed"} if sidebar.open == "closed" else None,
        main,
        sidebar.tag,
        sidebar.collapse_tag,
        sidebar_dependency(),
        _sidebar_init_js(),
        data_bslib_sidebar_init="true" if sidebar.open != "always" else None,
        data_bslib_sidebar_open=sidebar.open,
        data_bslib_sidebar_border=trinary(border),
        data_bslib_sidebar_border_radius=trinary(border_radius),
        style=css(
            __bslib_sidebar_width=as_css_unit(sidebar.width),
            __bslib_sidebar_bg=as_css_unit(sidebar.color_bg),
            __bslib_sidebar_fg=as_css_unit(sidebar.color_fg),
            __bs_card_border_color=border_color,
            height=as_css_unit(height),
            __bslib_sidebar_max_height_mobile=as_css_unit(max_height_mobile),
        ),
    )
    if fill:
        res = as_fill_item(res)

    return CardItem(res)


# TODO-maindocs; @add_example()
def sidebar_toggle(
    id: str,
    open: Literal["toggle", "open", "closed", "always"] | bool | None = None,
    session: Session | None = None,
) -> None:
    """
    Toggle a sidebar

    Toggle a :func:`~shiny.experimental.ui.sidebar` state during an active Shiny user session.

    Parameters
    ----------
    id
        The `id` of the :func:`~shiny.experimental.ui.sidebar` to toggle.
    open
        The desired state of the sidebar, choosing from the following options: `None`
        (toggle sidebar open and closed), `"open"` or `True` (open the sidebar),
        `"closed"` or `False` (close the sidebar). Note that `sidebar_toggle()` can only
        open or close the sidebar, so it does not support the `"desktop"` and `"always"`
    session
        A Shiny session object (the default should almost always be used).

    See Also
    --------
    * :func:`~shiny.experimental.ui.sidebar`
    * :func:`~shiny.experimental.ui.layout_sidebar`
    """
    session = require_active_session(session)

    method: Literal["toggle", "open", "close"]
    if open is None or open == "toggle":
        method = "toggle"
    elif open is True or open == "open":
        method = "open"
    elif open is False or open == "closed":
        method = "close"
    else:
        if open == "always" or open == "desktop":
            raise ValueError(
                f"`open = '{open}'` is not supported by `sidebar_toggle()`"
            )
        raise ValueError(
            "open must be NULL (or 'toggle'), TRUE (or 'open'), or FALSE (or 'closed')"
        )

    def callback() -> None:
        session.send_input_message(id, {"method": method})

    session.on_flush(callback, once=True)


_sidebar_func = sidebar


def _collapse_icon() -> Tag:
    return tags.svg(
        svgtags.path(
            fill_rule="evenodd",
            d="M1.646 4.646a.5.5 0 0 1 .708 0L8 10.293l5.646-5.647a.5.5 0 0 1 .708.708l-6 6a.5.5 0 0 1-.708 0l-6-6a.5.5 0 0 1 0-.708z",
        ),
        xmlns="http://www.w3.org/2000/svg",
        viewBox="0 0 16 16",
        class_="bi bi-chevron-down collapse-icon",
        style="fill:currentColor;",
        aria_hidden="true",
        role="img",
    )


def _sidebar_init_js() -> Tag:
    # Note: if we want to avoid inline `<script>` tags in the future for
    # initialization code, we might be able to do so by turning the sidebar layout
    # container into a web component
    return tags.script(
        {"data-bslib-sidebar-init": True},
        "bslib.Sidebar.initCollapsibleAll()",
    )


########################################################


# TODO: use class to single out sidebar value (in layout_sidebar)
def panel_sidebar(
    *args: TagChild | TagAttrs,
    width: int = 4,
    **kwargs: TagAttrValue,
) -> DeprecatedPanelSidebar:
    """Deprecated. Please use :func:`~shiny.experimental.ui.sidebar` instead of
    `ui.panel_sidebar()`."""
    # TODO-future: >= 2023-11-01; Add deprecation message below
    # Plan of action:
    # * No deprecation messages today (2023-05-18), and existing code _just works_.
    # * Change all examples to use the new API.
    # * In, say, 6 months, start emitting messages for code that uses the old API.

    # warn_deprecated("Please use `sidebar()` instead of `panel_sidebar()`. `panel_sidebar()` will go away in a future version of Shiny.")
    return DeprecatedPanelSidebar(
        *args,
        width=width,
        **kwargs,
    )


class DeprecatedPanelSidebar:
    """
    [Deprecated] Sidebar panel

    Class returned from :func:`~shiny.experimental.ui.panel_sidebar`. Please do not
    use this class and instead supply your content to
    :func:`~shiny.experimental.ui.layout_sidebar` directly.

    Parameters
    ----------
    *args
        Contents to the sidebar. Or tag attributes that are supplied to the resolved
        :class:`~htmltools.Tag` object.
    width
        An integeger between 1 and 12, inclusive, that determines the width of the
        sidebar. The default is 4.
    **kwargs
        Tag attributes that are supplied to the resolved :class:`~htmltools.Tag` object.

    Attributes
    ----------
    sidebar
        A output from :func:`~shiny.experimental.ui.sidebar`.

    See Also
    --------
    * :func:`~shiny.experimental.ui.layout_sidebar`
    * :func:`~shiny.experimental.ui.sidebar`
    """

    # Store `attrs` for `layout_sidebar()` to retrieve
    sidebar: Sidebar

    def __init__(
        self, *args: TagChild | TagAttrs, width: int = 4, **kwargs: TagAttrValue
    ) -> None:
        self.sidebar = sidebar(
            *args,
            width=f"{int(width / 12 * 100)}%",
            **kwargs,
        )

    # Hopefully this is never used. But wanted to try to be safe
    def tagify(self) -> Tag:
        """
        Tagify the `self.sidebar.tag` and return the result in a TagList
        """
        return self.sidebar.tag.tagify()


def panel_main(
    *args: TagChild | TagAttrs,
    width: int = 8,
    **kwargs: TagAttrValue,
) -> TagList | DeprecatedPanelMain:
    """Deprecated. Please supply `panel_main(*args)` directly to `layout_sidebar()`."""
    # TODO-future: >= 2023-11-01; Add deprecation message below
    # warn_deprecated(
    #     "Please supply `panel_main(*args)` directly to `layout_sidebar()`."
    # )
    # warn if keys are being ignored
    attrs, children = consolidate_attrs(*args, **kwargs)
    if len(attrs) > 0:
        return DeprecatedPanelMain(attrs=attrs, children=children)
        warn_deprecated(
            "`*args: TagAttrs` or `**kwargs: TagAttrValue` values supplied to `panel_main()` are being ignored. Please supply them directly to `layout_sidebar()`."
        )

    return TagList(*children)


class DeprecatedPanelMain:
    """
    [Deprecated] Main panel

    Class returned from :func:`~shiny.experimental.ui.panel_main`. Please do not use
    this class and instead supply your content to
    :func:`~shiny.experimental.ui.layout_sidebar` directly.


    Parameters
    ----------
    attrs
        Attributes to apply to the parent tag of the children.
    children
        Children UI Elements to render inside the parent tag.

    Attributes
    ----------
    attrs
        Attributes to apply to the parent tag of the children.
    children
        Children UI Elements to render inside the parent tag.

    See Also
    --------
    * :func:`~shiny.experimental.ui.layout_sidebar`
    * :func:`~shiny.experimental.ui.sidebar`
    """

    # Store `attrs` for `layout_sidebar()` to retrieve
    attrs: TagAttrs
    # Return `children` in `layout_sidebar()` via `.tagify()` method
    children: list[TagChild]

    def __init__(self, *, attrs: TagAttrs, children: list[TagChild]) -> None:
        self.attrs = attrs
        self.children = children

    def tagify(self) -> TagList:
        """
        Tagify the `children` and return the result in a TagList
        """
        return TagList(self.children).tagify()
