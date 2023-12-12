"Context manager components for Shiny Express"

from __future__ import annotations

from typing import Literal, Optional

from htmltools import Tag, TagAttrValue, TagChild, TagList

from ... import ui
from ...types import MISSING, MISSING_TYPE
from ...ui.css import CssUnit
from .. import _run
from .._recall_context import RecallContextManager

__all__ = (
    "set_page",
    "sidebar",
    "layout_sidebar",
    "layout_column_wrap",
    "column",
    "row",
    "card",
    "accordion",
    "accordion_panel",
    "navset",
    "navset_card",
    "nav",
    "panel_well",
    "panel_conditional",
    "panel_fixed",
    "panel_absolute",
    "page_fluid",
    "page_fixed",
    "page_fillable",
    "page_sidebar",
    "page_navbar",
)


# ======================================================================================
# Page functions
# ======================================================================================
def set_page(page_fn: RecallContextManager[Tag]):
    """Set the page function for the current Shiny express app."""
    _run.replace_top_level_recall_context_manager(page_fn, force=True)


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
        The initial state of the sidebar. It can be `"desktop"` (the sidebar starts open
        on desktop screen, closed on mobile), `"open"` or `True` (the sidebar starts
        open), `"closed"` or `False` (the sidebar starts closed), or `"always"` or
        `None` (the sidebar is always open and cannot be closed).

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
        may be one to four values. If one, then that value will be used for all four
        sides. If two, then the first value will be used for the top and bottom, while
        the second value will be used for left and right. If three, then the first will
        be used for top, the second will be left and right, and the third will be
        bottom. If four, then the values will be interpreted as top, right, bottom, and
        left respectively.
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


# TODO: Figure out sidebar arg for ui.layout_sidebar
def layout_sidebar(
    *,
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
):
    """
    Sidebar layout

    Create a sidebar layout component which can be dropped inside any Shiny UI page
    method (e.g. :func:`~shiny.shiny.ui.page_fillable`) or :func:`~shiny.ui.card`
    context.

    The first child needs to be of class :class:`~shiny.ui.Sidebar` object created by
    :func:`~shiny.express.ui.sidebar`. The remaining arguments will contain the contents
    to the main content area. Or tag attributes that are supplied to the resolved
    :class:`~htmltools.Tag` object.

    Parameters
    ----------
    fillable
        Whether or not the main content area should be wrapped in a fillable container.
        See :func:`~shiny.ui.as_fillable_container` for details.
    fill
        Whether or not the sidebar layout should be wrapped in a fillable container. See
        :func:`~shiny.ui.as_fill_item` for details.
    bg,fg
        A background or foreground color.
    border
        Whether or not to show a border around the sidebar layout.
    border_radius
        Whether or not to round the corners of the sidebar layout.
    border_color
        A border color.
    gap
        A CSS length unit defining the vertical `gap` (i.e., spacing) between elements
        provided to `*args`. This value will only be used if `fillable` is `True`.
    padding
        Padding within the sidebar itself. This can be a numeric vector (which will be
        interpreted as pixels) or a character vector with valid CSS lengths. `padding`
        may be one to four values. If one, then that value will be used for all four
        sides. If two, then the first value will be used for the top and bottom, while
        the second value will be used for left and right. If three, then the first will
        be used for top, the second will be left and right, and the third will be
        bottom. If four, then the values will be interpreted as top, right, bottom, and
        left respectively.
    height
        Any valid CSS unit to use for the height.
    """
    return RecallContextManager(
        ui.layout_sidebar,
        kwargs=dict(
            fillable=fillable,
            fill=fill,
            bg=bg,
            fg=fg,
            border=border,
            border_radius=border_radius,
            border_color=border_color,
            gap=gap,
            padding=padding,
            height=height,
            **kwargs,
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
        The desired width of each card. It can be a (unit-less) number between 0 and 1
        and should be specified as `1/num`, where `num` represents the number of desired
        columns. It can be a CSS length unit representing either the minimum (when
        `fixed_width=False`) or fixed width (`fixed_width=True`). It can also be `None`,
        which allows power users to set the `grid-template-columns` CSS property
        manually, either via a `style` attribute or a CSS stylesheet. If missing, a
        value of `200px` will be used.
    fixed_width
        When `width` is greater than 1 or is a CSS length unit, e.g. `"200px"`,
        `fixed_width` indicates whether that `width` value represents the absolute size
        of each column (`fixed_width=TRUE`) or the minimum size of a column
        (`fixed_width=FALSE`). When `fixed_width=FALSE`, new columns are added to a row
        when `width` space is available and columns will never exceed the container or
        viewport size. When `fixed_width=TRUE`, all columns will be exactly `width`
        wide, which may result in columns overflowing the parent container.
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
    wrapper
        A function (which returns a UI element) to call on unnamed arguments in `*args`
        which are not already card item(s) (like :func:`~shiny.ui.card_header`,
        :func:`~shiny.experimental.ui.card_body`, etc.). Note that non-card items are
        grouped together into one `wrapper` call (e.g. given `card("a", "b",
        card_body("c"), "d")`, `wrapper` would be called twice, once with `"a"` and
        `"b"` and once with `"d"`).
    **kwargs
        HTML attributes on the returned Tag.
    """
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
    *args
        A collection of nav items (e.g., :func:`shiny.ui.nav`).
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
    *args
        A collection of nav items (e.g., :func:`shiny.ui.nav`).
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


def nav(
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
        ui.nav,
        args=(title,),
        kwargs=dict(
            value=value,
            icon=icon,
        ),
    )


# ======================================================================================
# Value boxes
# ======================================================================================
def value_box(
    title: TagChild,
    value: TagChild,
    *,
    showcase: Optional[TagChild] = None,
    showcase_layout: ui._valuebox.SHOWCASE_LAYOUTS_STR
    | ui.ShowcaseLayout = "left center",
    full_screen: bool = False,
    theme: Optional[str | ui.ValueBoxTheme] = None,
    height: Optional[CssUnit] = None,
    max_height: Optional[CssUnit] = None,
    fill: bool = True,
    class_: Optional[str] = None,
    **kwargs: TagAttrValue,
):
    return RecallContextManager(
        ui.value_box,
        args=(title, value),
        kwargs=dict(
            showcase=showcase,
            showcase_layout=showcase_layout,
            full_screen=full_screen,
            theme=theme,
            height=height,
            max_height=max_height,
            fill=fill,
            class_=class_,
            **kwargs,
        ),
    )


# ======================================================================================
# Panels
# ======================================================================================


def panel_well(**kwargs: TagAttrValue):
    """
    Create a well panel

    This function wraps :func:`~shiny.ui.panel_well`.

    A well panel is a simple container with a border and some padding. It's useful for
    grouping related content together.
    """
    return RecallContextManager(
        ui.panel_well,
        kwargs=dict(
            **kwargs,
        ),
    )


def panel_conditional(
    *,
    condition: str,
    **kwargs: TagAttrValue,
):
    """
    Create a conditional panel

    This function wraps :func:`~shiny.ui.panel_conditional`.

    Show UI elements only if a ``JavaScript`` condition is ``true``.

    Parameters
    ----------
    condition
        A JavaScript expression that will be evaluated repeatedly to determine whether
        the panel should be displayed.
    **kwargs
        Attributes to place on the panel tag.

    Note
    ----
    In the JS expression, you can refer to input and output JavaScript objects that
    contain the current values of input and output. For example, if you have an input
    with an id of foo, then you can use input.foo to read its value. (Be sure not to
    modify the input/output objects, as this may cause unpredictable behavior.)

    You are not recommended to use special JavaScript characters such as a period . in
    the input id's, but if you do use them anyway, for example, ``id = "foo.bar"``, you
    will have to use ``input["foo.bar"]`` instead of ``input.foo.bar`` to read the input
    value.

    Tip
    ---
    A more powerful (but slower) way to conditionally show UI content is to use
    :func:`~shiny.render.ui`.
    """
    return RecallContextManager(
        ui.panel_conditional,
        kwargs=dict(
            condition=condition,
            **kwargs,
        ),
    )


def panel_fixed(
    *,
    top: Optional[str] = None,
    left: Optional[str] = None,
    right: Optional[str] = None,
    bottom: Optional[str] = None,
    width: Optional[str] = None,
    height: Optional[str] = None,
    draggable: bool = False,
    cursor: Literal["auto", "move", "default", "inherit"] = "auto",
    **kwargs: TagAttrValue,
):
    """
    Create a panel of absolutely positioned content.

    This function wraps :func:`~shiny.ui.panel_fixed`.

    This function is equivalent to calling :func:`~shiny.ui.panel_absolute` with
    ``fixed=True`` (i.e., the panel does not scroll with the rest of the page). See
    :func:`~shiny.ui.panel_absolute` for more information.

    Parameters
    ----------
    **kwargs
        Arguments passed along to :func:`~shiny.ui.panel_absolute`.

    See Also
    -------
    :func:`~shiny.ui.panel_absolute`
    """
    return RecallContextManager(
        ui.panel_fixed,
        kwargs=dict(
            top=top,
            left=left,
            right=right,
            bottom=bottom,
            width=width,
            height=height,
            draggable=draggable,
            cursor=cursor,
            **kwargs,
        ),
    )


def panel_absolute(
    *,
    top: Optional[str] = None,
    left: Optional[str] = None,
    right: Optional[str] = None,
    bottom: Optional[str] = None,
    width: Optional[str] = None,
    height: Optional[str] = None,
    draggable: bool = False,
    fixed: bool = False,
    cursor: Literal["auto", "move", "default", "inherit"] = "auto",
    **kwargs: TagAttrValue,
):
    """
    Create a panel of absolutely positioned content.

    This function wraps :func:`~shiny.ui.panel_absolute`.

    Creates a ``<div>`` tag whose CSS position is set to absolute (or fixed if ``fixed =
    True``). The way absolute positioning works in HTML is that absolute coordinates are
    specified relative to its nearest parent element whose position is not set to static
    (which is the default), and if no such parent is found, then relative to the page
    borders. If you're not sure what that means, just keep in mind that you may get
    strange results if you use this function from inside of certain types of panels.

    Parameters
    ----------
    top
        Distance between the top of the panel, and the top of the page or parent
        container.
    left
        Distance between the left side of the panel, and the left of the page or parent
        container.
    right
        Distance between the right side of the panel, and the right of the page or
        parent container.
    bottom
        Distance between the bottom of the panel, and the bottom of the page or parent
        container.
    width
        Width of the panel.
    height
        Height of the panel.
    draggable
        If ``True``, allows the user to move the panel by clicking and dragging.
    fixed
        Positions the panel relative to the browser window and prevents it from being
        scrolled with the rest of the page.
    cursor
        The type of cursor that should appear when the user mouses over the panel. Use
        ``"move"`` for a north-east-south-west icon, ``"default"`` for the usual cursor
        arrow, or ``"inherit"`` for the usual cursor behavior (including changing to an
        I-beam when the cursor is over text). The default is ``"auto"``, which is
        equivalent to ``"move" if draggable else "inherit"``.
    **kwargs
        Attributes added to the content's container tag.

    Tip
    ----
    The position (``top``, ``left``, ``right``, ``bottom``) and size (``width``,
    ``height``) parameters are all optional, but you should specify exactly two of top,
    bottom, and height and exactly two of left, right, and width for predictable
    results.

    Like most other distance parameters in Shiny, the position and size parameters take
    a number (interpreted as pixels) or a valid CSS size string, such as ``"100px"``
    (100 pixels) or ``"25%"``.

    For arcane HTML reasons, to have the panel fill the page or parent you should
    specify 0 for ``top``, ``left``, ``right``, and ``bottom`` rather than the more
    obvious ``width = "100%"`` and ``height = "100%"``.
    """
    return RecallContextManager(
        ui.panel_absolute,
        kwargs=dict(
            top=top,
            left=left,
            right=right,
            bottom=bottom,
            width=width,
            height=height,
            draggable=draggable,
            fixed=fixed,
            cursor=cursor,
            **kwargs,
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
    sidebar
        Content to display in the sidebar.
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
    """
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


# TODO: Figure out sidebar arg for ui.page_navbar
def page_navbar(
    *,
    title: Optional[str | Tag | TagList] = None,
    id: Optional[str] = None,
    selected: Optional[str] = None,
    fillable: bool | list[str] = True,
    fillable_mobile: bool = False,
    gap: Optional[CssUnit] = None,
    padding: Optional[CssUnit | list[CssUnit]] = None,
    position: Literal["static-top", "fixed-top", "fixed-bottom"] = "static-top",
    header: Optional[TagChild] = None,
    footer: Optional[TagChild] = None,
    bg: Optional[str] = None,
    inverse: bool = False,
    underline: bool = True,
    collapsible: bool = True,
    fluid: bool = True,
    window_title: str | MISSING_TYPE = MISSING,
    lang: Optional[str] = None,
):
    """
    Create a page with a navbar and a title.

    This function wraps :func:`~shiny.ui.page_navbar`.

    Parameters
    ----------
    title
        The browser window title (defaults to the host URL of the page). Can also be set
        as a side effect via :func:`~shiny.ui.panel_title`.
    id
        If provided, will create an input value that holds the currently selected nav
        item.
    selected
        Choose a particular nav item to select by default value (should match it's
        ``value``).
    sidebar
        A :func:`~shiny.ui.sidebar` component to display on every page.
    fillable
        Whether or not the main content area should be considered a fillable
        (i.e., flexbox) container.
    fillable_mobile
        Whether or not ``fillable`` should apply on mobile devices.
    position
        Determines whether the navbar should be displayed at the top of the page with
        normal scrolling behavior ("static-top"), pinned at the top ("fixed-top"), or
        pinned at the bottom ("fixed-bottom"). Note that using "fixed-top" or
        "fixed-bottom" will cause the navbar to overlay your body content, unless you
        add padding (e.g., ``tags.style("body {padding-top: 70px;}")``).
    header
        UI to display above the selected content.
    footer
        UI to display below the selected content.
    bg
        Background color of the navbar (a CSS color).
    inverse
        Either ``True`` for a light text color or ``False`` for a dark text color.
    collapsible
        ``True`` to automatically collapse the elements into an expandable menu on mobile devices or narrow window widths.
    fluid
        ``True`` to use fluid layout; ``False`` to use fixed layout.
    window_title
        The browser's window title (defaults to the host URL of the page). Can also be
        set as a side effect via :func:`~shiny.ui.panel_title`.
    lang
        ISO 639-1 language code for the HTML page, such as ``"en"`` or ``"ko"``. This
        will be used as the lang in the ``<html>`` tag, as in ``<html lang="en">``. The
        default, `None`, results in an empty string.

    See Also
    -------
    * :func:`~shiny.ui.nav`
    * :func:`~shiny.ui.nav_menu`
    * :func:`~shiny.ui.navset_bar`
    * :func:`~shiny.ui.page_fluid`

    Example
    -------
    See :func:`~shiny.ui.nav`.
    """

    return RecallContextManager(
        ui.page_navbar,
        kwargs=dict(
            title=title,
            id=id,
            selected=selected,
            fillable=fillable,
            fillable_mobile=fillable_mobile,
            gap=gap,
            padding=padding,
            position=position,
            header=header,
            footer=footer,
            bg=bg,
            inverse=inverse,
            underline=underline,
            collapsible=collapsible,
            fluid=fluid,
            window_title=window_title,
            lang=lang,
        ),
    )
