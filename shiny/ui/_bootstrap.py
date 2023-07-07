from __future__ import annotations

__all__ = (
    "row",
    "column",
    "layout_sidebar",
    "panel_well",
    "panel_sidebar",
    "panel_main",
    "panel_conditional",
    "panel_title",
    "panel_fixed",
    "panel_absolute",
    "help_text",
)


from typing import Literal, Optional

from htmltools import (
    Tag,
    TagAttrs,
    TagAttrValue,
    TagChild,
    Tagifiable,
    TagList,
    css,
    div,
    h2,
    span,
    tags,
)

from .._deprecated import warn_deprecated
from .._docstring import add_example
from ..module import current_namespace
from ..types import MISSING, MISSING_TYPE
from ._html_dependencies import jqui_deps
from ._utils import get_window_title
from ._x._sidebar import PanelMain as XPanelMain
from ._x._sidebar import PanelSidebar as XPanelSidebar
from ._x._sidebar import layout_sidebar as x_layout_sidebar
from ._x._utils import consolidate_attrs as x_consolidate_attrs


# TODO: make a python version of the layout guide?
@add_example()
def row(*args: TagChild | TagAttrs, **kwargs: TagAttrValue) -> Tag:
    """
    Responsive row-column based layout

    Layout UI components using Bootstrap's grid layout system. Use ``row()`` to group
    elements that should appear on the same line (if the browser has adequate width) and
    :func:`~shiny.ui.column` to define how much horizontal space within a 12-unit wide
    grid each on of these elements should occupy. See the [layout
    guide](https://shiny.posit.co/articles/layout-guide.html>) for more context and
    examples.
    (The article is about Shiny for R, but the general principles are the same.)

    Parameters
    ----------
    args
        Any number of child elements.
    kwargs
        Attributes to place on the row tag.

    Returns
    -------
    :
        A UI element.

    See Also
    -------
    :func:`~shiny.ui.column`
    """
    return div({"class": "row"}, *args, **kwargs)


def column(
    width: int, *args: TagChild | TagAttrs, offset: int = 0, **kwargs: TagAttrValue
) -> Tag:
    """
    Responsive row-column based layout

    See :func:`~shiny.ui.row` for more information.

    Parameters
    ----------
    width
        The width of the column (an integer between 1 and 12).
    args
        UI elements to place within the column.
    offset
        The number of columns to offset this column from the end of the previous column.
    kwargs
        Attributes to place on the column tag.

    Returns
    -------
    :
        A UI element.

    See Also
    -------
    :func:`~shiny.ui.row`
    """

    if width < 1 or width > 12:
        raise ValueError("Column width must be between 1 and 12")
    cls = "col-sm-" + str(width)
    if offset > 0:
        # offset-md-x is for bootstrap 4 forward compat
        # (every size tier has been bumped up one level)
        # https://github.com/twbs/bootstrap/blob/74b8fe7/docs/4.3/migration/index.html#L659
        off = str(offset)
        cls += f" offset-md-{off} col-sm-offset-{off}"
    return div({"class": cls}, *args, **kwargs)


@add_example()
def layout_sidebar(
    # TODO: also accept a generic list (and wrap in panel in that case)?
    sidebar: TagChild,
    main: TagChild,
    position: Literal["left", "right"] = "left",
) -> Tagifiable:
    """
    Layout a sidebar and main area

    Create a layout with a sidebar (:func:`~shiny.ui.panel_sidebar`) and main area
    (:func:`~shiny.ui.panel_main`). The sidebar is displayed with a distinct background
    color and typically contains input controls. By default, the main area occupies 2/3
    of the horizontal width and typically contains outputs.

    Parameters
    ----------
    sidebar
        A UI element to place in the sidebar (typically a
        :func:`~shiny.ui.panel_sidebar`)
    main
        A UI element to place in the main area (typically a
        :func:`~shiny.ui.panel_main`)
    position
        The position of the sidebar (left or right)

    Returns
    -------
    :
        A UI element

    See Also
    -------
    :func:`~shiny.ui.panel_sidebar`
    :func:`~shiny.ui.panel_main`
    """

    # Not requiring `XPanelSidebar`/`XPanelMain` to not expose the `_x` module if possible
    if not isinstance(sidebar, XPanelSidebar):
        sidebar = XPanelSidebar(sidebar)
    if not isinstance(main, XPanelMain):
        main = XPanelMain(attrs={}, children=[main])

    return x_layout_sidebar(
        sidebar.get_sidebar(position=position),
        main,
    )


def panel_well(*args: TagChild | TagAttrs, **kwargs: TagAttrValue) -> Tag:
    """
    Create a well panel

    Creates a panel with a slightly inset border and grey background. Equivalent to
    Bootstrap's ``well`` CSS class.

    Parameters
    ----------
    args
        UI elements to include inside the panel.
    kwargs
        Attributes to place on the panel tag.

    Returns
    -------
    :
        A UI element.

    See Also
    -------
    :func:`~shiny.ui.panel_sidebar`
    :func:`~shiny.ui.panel_main`
    """
    return div({"class": "well"}, *args, **kwargs)


def panel_sidebar(
    *args: TagChild | TagAttrs,
    width: int = 4,
    **kwargs: TagAttrValue,
) -> Tagifiable:
    """
    Create a sidebar panel

    See :func:`~shiny.ui.layout_sidebar` for more information and an example.

    Parameters
    ----------

    args
        UI elements to include inside the sidebar.
    width
        The width of the sidebar (an integer between 1 and 12)
    kwargs
        Attributes to place on the sidebar tag.

    Returns
    -------
    :
        A UI element.

    See Also
    -------
    :func:`~shiny.ui.panel_sidebar`
    :func:`~shiny.ui.panel_main`
    """
    return XPanelSidebar(*args, width=width, **kwargs)


def panel_main(
    *args: TagChild | TagAttrs,
    **kwargs: TagAttrValue,
) -> Tagifiable:
    """
    Create an main area panel

    See :func:`~shiny.ui.layout_sidebar` for more information and an example.

    Parameters
    ----------
    args
        UI elements to include inside the main area.
    kwargs
        Attributes to place on the main area tag.

    Returns
    -------
    :
        A UI element.

    See Also
    -------
    :func:`~shiny.ui.panel_sidebar`
    :func:`~shiny.ui.layout_sidebar`
    """
    attrs, children = x_consolidate_attrs(*args, **kwargs)
    if "width" in attrs:
        if attrs["width"] != 8:
            warn_deprecated(
                "panel_main(width=)` is being ignored. Given the sidebar width, the main panel will take up the remaining horizontal space."
            )
        del attrs["width"]

    if len(attrs) > 0:
        # While we could return an `XPanelMain()` for empty attrs,
        # let's try to limit the exposure of the class object
        return XPanelMain(attrs=attrs, children=children)

    return TagList(*children)


# TODO: replace `flowLayout()`/`splitLayout()` with a flexbox wrapper?
# def panel_input(*args: TagChild, **kwargs: TagAttr):
#  return div(flowLayout(...), class_="shiny-input-panel")


@add_example()
def panel_conditional(
    condition: str,
    *args: TagChild | TagAttrs,
    **kwargs: TagAttrValue,
) -> Tag:
    """
    Create a conditional panel

    Show UI elements only if a ``JavaScript`` condition is ``true``.

    Parameters
    ----------
    condition
        A JavaScript expression that will be evaluated repeatedly to determine whether
        the panel should be displayed.
    args
        UI elements to include inside the panel.
    kwargs
        Attributes to place on the panel tag.

    Returns
    -------
    :
        A UI element.

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

    See Also
    -------
    ~shiny.render.ui
    ~shiny.ui.output_ui
    """

    ns_prefix = current_namespace()

    if ns_prefix != "":
        ns_prefix += "-"

    return div(*args, data_display_if=condition, data_ns_prefix=ns_prefix, **kwargs)


@add_example()
def panel_title(
    title: str | Tag | TagList, window_title: str | MISSING_TYPE = MISSING
) -> TagList:
    """
    Create title(s) for the application.

    Parameters
    ----------
    title
        A title to display in the app's UI.
    window_title
        A title to display on the browser tab.

    Returns
    -------
    :
        A UI element.

    Note
    ----
    This result of this function causes a side effect of adding a title tag to the head
    of the document (this is necessary for the browser to display the title in the
    browser window). You can also specify a page title explicitly using the title
    parameter of the top-level page function (e.g., :func:`~shiny.ui.page_fluid`).
    """

    if isinstance(title, str):
        title = h2(title)

    return TagList(get_window_title(title, window_title), title)


def panel_fixed(*args: TagChild | TagAttrs, **kwargs: TagAttrValue) -> TagList:
    """
    Create a panel of absolutely positioned content.

    This function is equivalent to calling :func:`~shiny.ui.panel_absolute` with
    ``fixed=True`` (i.e., the panel does not scroll with the rest of the page). See
    :func:`~shiny.ui.panel_absolute` for more information.

    Parameters
    ----------
    args
        UI elements to include inside the panel.
    kwargs
        Arguments passed along to :func:`~shiny.ui.panel_absolute`.

    Returns
    -------
    :
        A UI element.

    See Also
    -------
    :func:`~shiny.ui.panel_absolute`
    """
    return panel_absolute(*args, fixed=True, **kwargs)


@add_example()
def panel_absolute(
    *args: TagChild | TagAttrs,
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
) -> TagList:
    """
    Create a panel of absolutely positioned content.

    Creates a ``<div>`` tag whose CSS position is set to absolute (or fixed if ``fixed =
    True``). The way absolute positioning works in HTML is that absolute coordinates are
    specified relative to its nearest parent element whose position is not set to static
    (which is the default), and if no such parent is found, then relative to the page
    borders. If you're not sure what that means, just keep in mind that you may get
    strange results if you use this function from inside of certain types of panels.

    Parameters
    ----------
    args
        UI elements to include inside the panel.
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
    kwargs
        Attributes added to the content's container tag.

    Returns
    -------
    :
        A UI element

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

    style = css(
        top=top,
        left=left,
        right=right,
        bottom=bottom,
        width=width,
        height=height,
        position="fixed" if fixed else "absolute",
        cursor="move" if draggable else "inherit" if cursor == "auto" else cursor,
    )
    divTag = div(*args, style=style, **kwargs)
    if not draggable:
        return TagList(divTag)
    divTag.add_class("draggable")
    deps = jqui_deps()
    deps.stylesheet = []
    return TagList(deps, divTag, tags.script('$(".draggable").draggable();'))


def help_text(*args: TagChild | TagAttrs, **kwargs: TagAttrValue) -> Tag:
    """
    Create a help text element

    Parameters
    ----------
    args
        UI elements to include inside the help text.
    kwargs
        Attributes to add to the text container.

    Returns
    -------
    :
        A UI element
    """

    return span({"class": "help-block"}, *args, **kwargs)
