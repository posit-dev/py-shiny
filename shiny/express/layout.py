from __future__ import annotations

from typing import Literal, Optional

import htmltools
from htmltools import Tag, TagAttrValue, TagChild, TagList

from .. import ui
from ..types import MISSING, MISSING_TYPE
from ..ui._layout_columns import BreakpointsUser
from ..ui.css import CssUnit
from . import _run
from ._recall_context import RecallContextManager, wrap_recall_context_manager

__all__ = (
    "set_page",
    "p",
    "div",
    "span",
    "pre",
    "sidebar",
    "layout_column_wrap",
    "layout_columns",
    "column",
    "row",
    "card",
    "accordion",
    "accordion_panel",
    "navset",
    "navset_card",
    "nav_panel",
    "page_fluid",
    "page_fixed",
    "page_fillable",
    "page_sidebar",
)


# ======================================================================================
# Page functions
# ======================================================================================
def set_page(page_fn: RecallContextManager[Tag]):
    """Set the page function for the current Shiny express app."""
    _run.replace_top_level_recall_context_manager(page_fn, force=True)


# ======================================================================================
# htmltools Tag functions
# ======================================================================================
p = wrap_recall_context_manager(htmltools.p)
div = wrap_recall_context_manager(htmltools.div)
span = wrap_recall_context_manager(htmltools.span)
pre = wrap_recall_context_manager(htmltools.pre)


# ======================================================================================
# Shiny layout components
# ======================================================================================
def sidebar(
    *,
    width: CssUnit = 250,
    position: Literal["left", "right"] = "left",
    open: Literal["desktop", "open", "closed", "always"] = "always",
    id: Optional[str] = None,
    title: TagChild | str = None,
    bg: Optional[str] = None,
    fg: Optional[str] = None,
    class_: Optional[str] = None,  # TODO-future; Consider using `**kwargs` instead
    max_height_mobile: Optional[str | float] = "auto",
    gap: Optional[CssUnit] = None,
    padding: Optional[CssUnit | list[CssUnit]] = None,
) -> RecallContextManager[ui.Sidebar]:
    """
    Sidebar element

    Create a collapsing sidebar layout. This function wraps :func:`~shiny.ui.sidebar`.

    Parameters
    ----------
    width
        A valid CSS unit used for the width of the sidebar.
    position
        Where the sidebar should appear relative to the main content.
    open
        The initial state of the sidebar.

        * `"desktop"`: the sidebar starts open on desktop screen, closed on mobile
        * `"open"` or `True`: the sidebar starts open
        * `"closed"` or `False`: the sidebar starts closed
        * `"always"` or `None`: the sidebar is always open and cannot be closed

        In :func:`~shiny.ui.update_sidebar`, `open` indicates the desired state of the
        sidebar. Note that :func:`~shiny.ui.update_sidebar` can only open or close the
        sidebar, so it does not support the `"desktop"` and `"always"` options.
    id
        A character string. Required if wanting to re-actively read (or update) the
        `collapsible` state in a Shiny app.
    title
        A character title to be used as the sidebar title, which will be wrapped in a
        `<div>` element with class `sidebar-title`. You can also provide a custom
        :class:`~htmltools.Tag` for the title element, in which case you'll
        likely want to give this element `class = "sidebar-title"`.
    bg,fg
        A background or foreground color.
    class_
        CSS classes for the sidebar container element, in addition to the fixed
        `.sidebar` class.
    max_height_mobile
        A CSS length unit (passed through :func:`~shiny.ui.css.as_css_unit`) defining
        the maximum height of the horizontal sidebar when viewed on mobile devices. Only
        applies to always-open sidebars that use `open = "always"`, where by default the
        sidebar container is placed below the main content container on mobile devices.
    gap
        A CSS length unit defining the vertical `gap` (i.e., spacing) between elements
        provided to `*args`.
    padding
        Padding within the sidebar itself. This can be a numeric vector (which will be
        interpreted as pixels) or a character vector with valid CSS lengths. `padding`
        may be one to four values.

        * If a single value, then that value will be used for all four sides.
        * If two, then the first value will be used for the top and bottom, while
          the second value will be used for left and right.
        * If three values, then the first will be used for top, the second will be left
          and right, and the third will be bottom.
        * If four, then the values will be interpreted as top, right, bottom, and left
          respectively.

    Returns
    -------
    :
        A :class:`~shiny.ui.Sidebar` object.
    """
    return RecallContextManager(
        ui.sidebar,
        default_page=page_sidebar(),
        kwargs=dict(
            width=width,
            position=position,
            open=open,
            id=id,
            title=title,
            bg=bg,
            fg=fg,
            class_=class_,
            max_height_mobile=max_height_mobile,
            gap=gap,
            padding=padding,
        ),
    )


def layout_column_wrap(
    *,
    width: CssUnit | None | MISSING_TYPE = MISSING,
    fixed_width: bool = False,
    heights_equal: Literal["all", "row"] = "all",
    fill: bool = True,
    fillable: bool = True,
    height: Optional[CssUnit] = None,
    height_mobile: Optional[CssUnit] = None,
    gap: Optional[CssUnit] = None,
    class_: Optional[str] = None,
    **kwargs: TagAttrValue,
):
    """
    A grid-like, column-first layout

    Wraps a 1d sequence of UI elements into a 2d grid. The number of columns (and rows)
    in the grid dependent on the column `width` as well as the size of the display.
    This function wraps :func:`~shiny.ui.layout_column_wrap`.

    Parameters
    ----------
    width
        The desired width of each card. It can be one of the following:

        * A (unit-less) number between 0 and 1, specified as `1/num`, where `num`
          represents the number of desired columns.
        * A CSS length unit representing either the minimum (when `fixed_width=False`)
          or fixed width (`fixed_width=True`).
        * `None`, which allows power users to set the `grid-template-columns` CSS
          property manually, either via a `style` attribute or a CSS stylesheet.
        * If missing, a value of `200px` will be used.
    fixed_width
        When `width` is greater than 1 or is a CSS length unit, e.g. `"200px"`,
        `fixed_width` indicates whether that `width` value represents the absolute size
        of each column (`fixed_width=TRUE`) or the minimum size of a column
        (`fixed_width=FALSE`).

        When `fixed_width=FALSE`, new columns are added to a row when `width` space is
        available and columns will never exceed the container or viewport size.

        When `fixed_width=TRUE`, all columns will be exactly `width` wide, which may
        result in columns overflowing the parent container.
    heights_equal
        If `"all"` (the default), every card in every row of the grid will have the same
        height. If `"row"`, then every card in _each_ row of the grid will have the same
        height, but heights may vary between rows.
    fill
        Whether or not to allow the layout to grow/shrink to fit a fillable container
        with an opinionated height (e.g., :func:`~shiny.ui.page_fillable`).
    fillable
        Whether or not each element is wrapped in a fillable container.
    height
        Any valid CSS unit to use for the height.
    height_mobile
        Any valid CSS unit to use for the height when on mobile devices (or narrow
        windows).
    gap
        Any valid CSS unit to use for the gap between columns.
    class_
        A CSS class to apply to the containing element.
    **kwargs
        Additional attributes to apply to the containing element.

    Returns
    -------
    :
        A :class:`~htmltools.Tag` element.

    See Also
    --------
    * :func:`~shiny.express.layout.layout_columns` for laying out elements into a
      responsive 12-column grid.
    """
    return RecallContextManager(
        ui.layout_column_wrap,
        default_page=page_fillable(),
        kwargs=dict(
            width=width,
            fixed_width=fixed_width,
            heights_equal=heights_equal,
            fill=fill,
            fillable=fillable,
            height=height,
            height_mobile=height_mobile,
            gap=gap,
            class_=class_,
            **kwargs,
        ),
    )


def layout_columns(
    *,
    col_widths: BreakpointsUser[int] = None,
    row_heights: BreakpointsUser[CssUnit] = None,
    fill: bool = True,
    fillable: bool = True,
    gap: Optional[CssUnit] = None,
    class_: Optional[str] = None,
    height: Optional[CssUnit] = None,
    **kwargs: TagAttrValue,
):
    """
    Create responsive, column-based grid layouts, based on a 12-column grid.

    Parameters
    ----------
    col_widths
        The widths of the columns, possibly at different breakpoints. Can be one of the
        following:

        * `None` (the default): Automatically determines a sensible number of columns
          based on the number of children given to the layout.
        * A list or tuple of integers between 1 and 12, where each element represents
          the number of columns for the relevant UI element. Column widths are recycled
          to extend the values in `col_widths` to match the actual number of items in
          the layout, and children are wrapped onto the next row when a row exceeds 12
          column units. For example, `col_widths=(4, 8, 12)` allocates 4 columns to the
          first element, 8 columns to the second element, and 12 columns to the third
          element (which wraps to the next row). Negative values are also allowed, and
          are treated as empty columns. For example, `col_widths=(-2, 8, -2)` would
          allocate 8 columns to an element (with 2 empty columns on either side).
        * A dictionary of column widths at different breakpoints. The keys should be
          one of `"xs"`, `"sm"`, `"md"`, `"lg"`, `"xl"`, or `"xxl"`, and the values are
          either of the above. For example, `col_widths={"sm": (3, 3, 6), "lg": (4)}`.

    row_heights
        The heights of the rows, possibly at different breakpoints. Can be one of the
        following:

        * A numeric vector, where each value represents the
          [fractional unit](https://css-tricks.com/introduction-fr-css-unit/)
          (`fr`) height of the relevant row. If there are more rows than values
          provided, the pattern will be repeated. For example, `row_heights=(1, 2)`
          allows even rows to take up twice as much space as odd rows.
        * A list of numeric or CSS length units, where each value represents the height
          of the relevant row. If more rows are needed than values provided, the pattern
          will repeat. For example, `row_heights=["auto", 1]` allows the height of odd
          rows to be driven my it's contents and even rows to be
          [`1fr`](https://css-tricks.com/introduction-fr-css-unit/).
        * A single string containing CSS length units. In this case, the value is
          supplied directly to `grid-auto-rows`.
        * A dictionary of row heights at different breakpoints, where each key is a
          breakpoint name (one of `"xs"`, `"sm"`, `"md"`, `"lg"`, `"xl"`, or `"xxl"`)
          and where the values may be any of the above options.

    fill
        Whether or not to allow the layout to grow/shrink to fit a fillable container
        with an opinionated height (e.g., :func:`~shiny.ui.page_fillable`).

    fillable
        Whether or not each element is wrapped in a fillable container.

    gap
        Any valid CSS unit to use for the gap between columns.

    class_
        CSS class(es) to apply to the containing element.

    height
        Any valid CSS unit to use for the height.

    **kwargs
        Additional attributes to apply to the containing element.

    Returns
    -------
    :
        An :class:`~htmltools.Tag` element.

    See Also
    --------
    * :func:`~shiny.express.layout.layout_column_wrap` for laying out elements into a
      uniform grid.

    Reference
    --------
    * [Bootstrap CSS Grid](https://getbootstrap.com/docs/5.3/layout/grid/)
    * [Bootstrap Breakpoints](https://getbootstrap.com/docs/5.3/layout/breakpoints/)
    """
    return RecallContextManager(
        ui.layout_columns,
        kwargs=dict(
            col_widths=col_widths,
            row_heights=row_heights,
            fill=fill,
            fillable=fillable,
            gap=gap,
            class_=class_,
            height=height,
            **kwargs,
        ),
    )


def column(width: int, *, offset: int = 0, **kwargs: TagAttrValue):
    """
    Responsive row-column based layout

    This function wraps :func:`~shiny.ui.column`. See :func:`~shiny.ui.row` for more
    information.

    Parameters
    ----------
    width
        The width of the column (an integer between 1 and 12).
    offset
        The number of columns to offset this column from the end of the previous column.
    **kwargs
        Attributes to place on the column tag.

    Returns
    -------
    :
        A UI element.

    See Also
    -------
    :func:`~shiny.ui.row`
    """
    return RecallContextManager(
        ui.column,
        args=(width,),
        kwargs=dict(
            offset=offset,
            **kwargs,
        ),
    )


def row(**kwargs: TagAttrValue):
    """
    Responsive row-column based layout

    This function wraps :func:`~shiny.ui.row`. Layout UI components using Bootstrap's
    grid layout system. Use ``row()`` to group elements that should appear on the same
    line (if the browser has adequate width) and :func:`~shiny.ui.column` to define how
    much horizontal space within a 12-unit wide grid each on of these elements should
    occupy. See the [layout guide](https://shiny.posit.co/articles/layout-guide.html>)
    for more context and examples. (The article is about Shiny for R, but the general
    principles are the same.)

    Parameters
    ----------
    **kwargs
        Attributes to place on the row tag.

    Returns
    -------
    :
        A UI element.

    See Also
    -------
    :func:`~shiny.ui.column`
    """
    return RecallContextManager(ui.row, kwargs=kwargs)


def card(
    *,
    full_screen: bool = False,
    height: Optional[CssUnit] = None,
    max_height: Optional[CssUnit] = None,
    min_height: Optional[CssUnit] = None,
    fill: bool = True,
    class_: Optional[str] = None,
    **kwargs: TagAttrValue,
):
    """
    A Bootstrap card component

    This function wraps :func:`~shiny.ui.card`. A general purpose container for grouping
    related UI elements together with a border and optional padding. To learn more about
    `card()`s, see [this article](https://rstudio.github.io/bslib/articles/cards.html).

    Parameters
    ----------
    full_screen
        If `True`, an icon will appear when hovering over the card body. Clicking the
        icon expands the card to fit viewport size.
    height,max_height,min_height
        Any valid CSS unit (e.g., `height="200px"`). Doesn't apply when a card is made
        `full_screen` (in this case, consider setting a `height` in
        :func:`~shiny.experimental.ui.card_body`).
    fill
        Whether or not to allow the card to grow/shrink to fit a fillable container with
        an opinionated height (e.g., :func:`~shiny.ui.page_fillable`).
    class_
        Additional CSS classes for the returned Tag.
    **kwargs
        HTML attributes on the returned Tag.

    Returns
    -------
    :
        An :func:`~shiny.ui.tags.div` tag.
    """

    # wrapper
    #     A function (which returns a UI element) to call on unnamed arguments in `*args`
    #     which are not already card item(s) (like :func:`~shiny.ui.card_header`,
    #     :func:`~shiny.experimental.ui.card_body`, etc.). Note that non-card items are
    #     grouped together into one `wrapper` call (e.g. given `card("a", "b",
    #     card_body("c"), "d")`, `wrapper` would be called twice, once with `"a"` and
    #     `"b"` and once with `"d"`).

    return RecallContextManager(
        ui.card,
        kwargs=dict(
            full_screen=full_screen,
            height=height,
            max_height=max_height,
            min_height=min_height,
            fill=fill,
            class_=class_,
            **kwargs,
        ),
    )


def accordion(
    *,
    id: Optional[str] = None,
    open: Optional[bool | str | list[str]] = None,
    multiple: bool = True,
    class_: Optional[str] = None,
    width: Optional[CssUnit] = None,
    height: Optional[CssUnit] = None,
    **kwargs: TagAttrValue,
):
    """
    Create a vertically collapsing accordion.

    This function wraps :func:`~shiny.ui.accordion`.

    Parameters
    ----------
    id
        If provided, you can use `input.id()` in your server logic to determine which of
        the :func:`~shiny.ui.accordion_panel`s are currently active. The
        value will correspond to the :func:`~shiny.ui.accordion_panel`'s
        `value` argument.
    open
        A list of :func:`~shiny.ui.accordion_panel` values to open (i.e.,
        show) by default. The default value of `None` will open the first
        :func:`~shiny.ui.accordion_panel`. Use a value of `True` to open
        all (or `False` to open none) of the items. It's only possible to open more than
        one panel when `multiple=True`.
    multiple
        Whether multiple :func:`~shiny.ui.accordion_panel` can be open at
        once.
    class_
        Additional CSS classes to include on the accordion div.
    width
        Any valid CSS unit; for example, height="100%".
    height
        Any valid CSS unit; for example, height="100%".
    **kwargs
        Attributes to this tag.

    Returns
    -------
    :
        Accordion panel Tag object.
    """
    return RecallContextManager(
        ui.accordion,
        kwargs=dict(
            id=id,
            open=open,
            multiple=multiple,
            class_=class_,
            width=width,
            height=height,
            **kwargs,
        ),
    )


def accordion_panel(
    title: TagChild,
    *,
    value: Optional[str] | MISSING_TYPE = MISSING,
    icon: Optional[TagChild] = None,
    **kwargs: TagAttrValue,
):
    """
    Single accordion panel.

    This function wraps :func:`~shiny.ui.accordion_panel`.

    Parameters
    ----------
    title
        A title to appear in the :func:`~shiny.ui.accordion_panel`'s header.
    value
        A character string that uniquely identifies this panel. If `MISSING`, the
        `title` will be used.
    icon
        A :class:`~htmltools.Tag` which is positioned just before the `title`.
    **kwargs
        Tag attributes to the `accordion-body` div Tag.

    Returns
    -------
    :
        `AccordionPanel` object.
    """
    return RecallContextManager(
        ui.accordion_panel,
        args=(title,),
        kwargs=dict(
            value=value,
            icon=icon,
            **kwargs,
        ),
    )


# ======================================================================================
# Nav components
# ======================================================================================


def navset(
    *,
    type: Literal["underline", "pill", "tab"] = "underline",
    id: Optional[str] = None,
    selected: Optional[str] = None,
    header: TagChild = None,
    footer: TagChild = None,
):
    """
    Render a set of nav items

    Parameters
    ----------
    type
        The type of navset to render. Can be one of `"underline"`, `"pill"`, or `"tab"`.
    id
        If provided, will create an input value that holds the currently selected nav
        item.
    selected
        Choose a particular nav item to select by default value (should match it's
        ``value``).
    header
        UI to display above the selected content.
    footer
        UI to display below the selected content.
    """
    # *args
    #     A collection of nav items (e.g., :func:`shiny.ui.nav`).

    funcs = {
        "underline": ui.navset_underline,
        "pill": ui.navset_pill,
        "tab": ui.navset_tab,
    }

    func = funcs.get(type, None)
    if func is None:
        raise ValueError(f"Invalid navset type: {type!r}")

    return RecallContextManager(
        func,
        kwargs=dict(
            id=id,
            selected=selected,
            header=header,
            footer=footer,
        ),
    )


def navset_card(
    *,
    type: Literal["underline", "pill", "tab"] = "underline",
    id: Optional[str] = None,
    selected: Optional[str] = None,
    title: Optional[TagChild] = None,
    sidebar: Optional[ui.Sidebar] = None,
    header: TagChild = None,
    footer: TagChild = None,
):
    """
    Render a set of nav items inside a card container.

    Parameters
    ----------
    type
        The type of navset to render. Can be one of `"underline"`, `"pill"`, or `"tab"`.
    id
        If provided, will create an input value that holds the currently selected nav
        item.
    selected
        Choose a particular nav item to select by default value (should match it's
        ``value``).
    sidebar
        A :class:`shiny.ui.Sidebar` component to display on every :func:`~shiny.ui.nav` page.
    header
        UI to display above the selected content.
    footer
        UI to display below the selected content.
    """
    # *args
    #     A collection of nav items (e.g., :func:`shiny.ui.nav`).

    funcs = {
        "underline": ui.navset_card_underline,
        "pill": ui.navset_card_pill,
        "tab": ui.navset_card_tab,
    }

    func = funcs.get(type, None)
    if func is None:
        raise ValueError(f"Invalid navset type: {type!r}")

    return RecallContextManager(
        func,
        kwargs=dict(
            id=id,
            selected=selected,
            title=title,
            sidebar=sidebar,
            header=header,
            footer=footer,
        ),
    )


def nav_panel(
    title: TagChild,
    *,
    value: Optional[str] = None,
    icon: TagChild = None,
):
    """
    Create a nav item pointing to some internal content.

    This function wraps :func:`~shiny.ui.nav`.

    Parameters
    ----------
    title
        A title to display. Can be a character string or UI elements (i.e., tags).
    value
        The value of the item. This is used to determine whether the item is active
        (when an ``id`` is provided to the nav container), programmatically select the
        item (e.g., :func:`~shiny.ui.update_navs`), and/or be provided to the
        ``selected`` argument of the navigation container (e.g.,
        :func:`~shiny.ui.navset_tab`).
    icon
        An icon to appear inline with the button/link.
    """
    return RecallContextManager(
        ui.nav_panel,
        args=(title,),
        kwargs=dict(
            value=value,
            icon=icon,
        ),
    )


# ======================================================================================
# Page components
# ======================================================================================
def page_fluid(
    *,
    title: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: str,
) -> RecallContextManager[Tag]:
    """
    Create a fluid page.

    This function wraps :func:`~shiny.ui.page_fluid`.

    Parameters
    ----------
    title
        The browser window title (defaults to the host URL of the page). Can also be set
        as a side effect via :func:`~shiny.ui.panel_title`.
    lang
        ISO 639-1 language code for the HTML page, such as ``"en"`` or ``"ko"``. This
        will be used as the lang in the ``<html>`` tag, as in ``<html lang="en">``. The
        default, `None`, results in an empty string.
    **kwargs
        Attributes on the page level container.

    Returns
    -------
    :
        A UI element.
    """
    return RecallContextManager(
        ui.page_fluid,
        kwargs=dict(
            title=title,
            lang=lang,
            **kwargs,
        ),
    )


def page_fixed(
    *,
    title: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: str,
) -> RecallContextManager[Tag]:
    """
    Create a fixed page.

    This function wraps :func:`~shiny.ui.page_fixed`.

    Parameters
    ----------
    title
        The browser window title (defaults to the host URL of the page). Can also be set
        as a side effect via :func:`~shiny.ui.panel_title`.
    lang
        ISO 639-1 language code for the HTML page, such as ``"en"`` or ``"ko"``. This
        will be used as the lang in the ``<html>`` tag, as in ``<html lang="en">``. The
        default, `None`, results in an empty string.
    **kwargs
        Attributes on the page level container.

    Returns
    -------
    :
        A UI element.
    """
    return RecallContextManager(
        ui.page_fixed,
        kwargs=dict(
            title=title,
            lang=lang,
            **kwargs,
        ),
    )


def page_fillable(
    *,
    padding: Optional[CssUnit | list[CssUnit]] = None,
    gap: Optional[CssUnit] = None,
    fillable_mobile: bool = False,
    title: Optional[str] = None,
    lang: Optional[str] = None,
    **kwargs: TagAttrValue,
):
    """
    Creates a fillable page.

    This function wraps :func:`~shiny.ui.page_fillable`.

    Parameters
    ----------
    padding
        Padding to use for the body. See :func:`~shiny.ui.css_unit.as_css_padding`
        for more details.
    fillable_mobile
        Whether or not the page should fill the viewport's height on mobile devices
        (i.e., narrow windows).
    gap
        A CSS length unit passed through :func:`~shiny.ui.css_unit.as_css_unit`
        defining the `gap` (i.e., spacing) between elements provided to `*args`.
    title
        The browser window title (defaults to the host URL of the page). Can also be set
        as a side effect via :func:`~shiny.ui.panel_title`.
    lang
        ISO 639-1 language code for the HTML page, such as ``"en"`` or ``"ko"``. This
        will be used as the lang in the ``<html>`` tag, as in ``<html lang="en">``. The
        default, `None`, results in an empty string.

    Returns
    -------
    :
        A UI element.
    """
    return RecallContextManager(
        ui.page_fillable,
        kwargs=dict(
            padding=padding,
            gap=gap,
            fillable_mobile=fillable_mobile,
            title=title,
            lang=lang,
            **kwargs,
        ),
    )


def page_sidebar(
    *,
    title: Optional[str | Tag | TagList] = None,
    fillable: bool = True,
    fillable_mobile: bool = False,
    window_title: str | MISSING_TYPE = MISSING,
    lang: Optional[str] = None,
    **kwargs: TagAttrValue,
):
    """
    Create a page with a sidebar and a title.

    This function wraps :func:`~shiny.ui.page_sidebar`.

    Parameters
    ----------
    title
        A title to display at the top of the page.
    fillable
        Whether or not the main content area should be considered a fillable
        (i.e., flexbox) container.
    fillable_mobile
        Whether or not ``fillable`` should apply on mobile devices.
    window_title
        The browser's window title (defaults to the host URL of the page). Can also be
        set as a side effect via :func:`~shiny.ui.panel_title`.
    lang
        ISO 639-1 language code for the HTML page, such as ``"en"`` or ``"ko"``. This
        will be used as the lang in the ``<html>`` tag, as in ``<html lang="en">``. The
        default, `None`, results in an empty string.
    **kwargs
        Additional attributes passed to :func:`~shiny.ui.layout_sidebar`.

    Returns
    -------
    :
        A UI element.
    """
    # sidebar
    #     Content to display in the sidebar.

    return RecallContextManager(
        ui.page_sidebar,
        kwargs=dict(
            title=title,
            fillable=fillable,
            fillable_mobile=fillable_mobile,
            window_title=window_title,
            lang=lang,
            **kwargs,
        ),
    )
