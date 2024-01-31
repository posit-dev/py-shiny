from __future__ import annotations

__all__ = (
    "row",
    "column",
    "panel_well",
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
    TagList,
    css,
    div,
    h2,
    span,
    tags,
)

from .._docstring import add_example, no_example
from ..module import current_namespace
from ..types import MISSING, MISSING_TYPE
from ._html_deps_external import jqui_deps
from ._utils import get_window_title


# TODO: make a python version of the layout guide?
@add_example()
def row(*args: TagChild | TagAttrs, **kwargs: TagAttrValue) -> Tag:
    """
    Responsive row-column based layout

    Layout UI components using Bootstrap's grid layout system. Use ``row()`` to group
    elements that should appear on the same line (if the browser has adequate width) and
    :func:`~shiny.ui.column` to define how much horizontal space within a 12-unit wide
    grid each on of these elements should occupy. See the [layout
    guide](https://shiny.posit.co/articles/layout-guide.html) for more context and
    examples.
    (The article is about Shiny for R, but the general principles are the same.)

    Parameters
    ----------
    *args
        Any number of child elements.
    **kwargs
        Attributes to place on the row tag.

    Returns
    -------
    :
        A UI element.

    See Also
    --------
    * :func:`~shiny.ui.column`
    """
    return div({"class": "row"}, *args, **kwargs)


@add_example(ex_dir="../api-examples/row")
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
    *args
        UI elements to place within the column.
    offset
        The number of columns to offset this column from the end of the previous column.
    **kwargs
        Attributes to place on the column tag.

    Returns
    -------
    :
        A UI element.

    See Also
    --------
    * :func:`~shiny.ui.row`
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


@no_example()
def panel_well(*args: TagChild | TagAttrs, **kwargs: TagAttrValue) -> Tag:
    """
    Create a well panel.

    Creates a panel with a slightly inset border and gray background. Equivalent to
    Bootstrap's ``well`` CSS class.

    Parameters
    ----------
    *args
        UI elements to include inside the panel.
    **kwargs
        Attributes to place on the panel tag.

    Returns
    -------
    :
        A UI element.

    See Also
    --------
    * :func:`~shiny.ui.panel_sidebar`
    * :func:`~shiny.ui.panel_main`
    """
    return div({"class": "well"}, *args, **kwargs)


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
    Create a conditional panel.

    Show UI elements only if a ``JavaScript`` condition is ``true``.

    Parameters
    ----------
    condition
        A JavaScript expression that will be evaluated repeatedly to determine whether
        the panel should be displayed.
    *args
        UI elements to include inside the panel.
    **kwargs
        Attributes to place on the panel tag.

    Returns
    -------
    :
        A UI element.

    Note
    ----
    In the JS expression, you can refer to input and output JavaScript objects that
    contain the current values of input and output. For example, if you have an input
    with an ``id`` of ``foo``, then you can use ``input.foo`` to read its value.
    (Be sure not to modify the input/output objects, as this may cause unpredictable
    behavior.)

    You are not recommended to use special JavaScript characters such as a period . in
    the input id's, but if you do use them anyway, for example, `id = "foo.bar"`, you
    will have to use `input["foo.bar"]` instead of ``input.foo.bar`` to read the input
    value.

    Tip
    ---
    A more powerful (but slower) way to conditionally show UI content is to use
    :class:`~shiny.render.ui`.

    See Also
    --------
    * :class:`~shiny.render.ui`
    * :func:`~shiny.ui.output_ui`
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


@no_example()
def panel_fixed(
    *args: TagChild | TagAttrs,
    top: Optional[str] = None,
    left: Optional[str] = None,
    right: Optional[str] = None,
    bottom: Optional[str] = None,
    width: Optional[str] = None,
    height: Optional[str] = None,
    draggable: bool = False,
    cursor: Literal["auto", "move", "default", "inherit"] = "auto",
    **kwargs: TagAttrValue,
) -> TagList:
    """
    Create a panel of absolutely positioned content.

    This function is equivalent to calling :func:`~shiny.ui.panel_absolute` with
    ``fixed=True`` (i.e., the panel does not scroll with the rest of the page). See
    :func:`~shiny.ui.panel_absolute` for more information.

    Parameters
    ----------
    *args
        UI elements to include inside the panel.
    **kwargs
        Arguments passed along to :func:`~shiny.ui.panel_absolute`.

    Returns
    -------
    :
        A UI element.

    See Also
    --------
    * :func:`~shiny.ui.panel_absolute`
    """
    return panel_absolute(
        *args,
        top=top,
        left=left,
        right=right,
        bottom=bottom,
        width=width,
        height=height,
        draggable=draggable,
        cursor=cursor,
        fixed=True,
        **kwargs,
    )


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

    Creates a `<div>` tag whose CSS position is set to absolute (or fixed if ``fixed =
    True``). In HTML, absolute coordinates are specified relative to an element's
    nearest parent element whose position is not set to static (the default).
    If no such parent is found, the coordinates are relative to the page borders.
    If you're not sure what that means, just keep in mind that you may get
    strange results if you use this function from inside of certain types of panels.

    Parameters
    ----------
    *args
        UI elements to include inside the panel.
    top
        Distance between the top of the panel and the top of the page or parent
        container.
    left
        Distance between the left side of the panel and the left of the page or parent
        container.
    right
        Distance between the right side of the panel and the right of the page or
        parent container.
    bottom
        Distance between the bottom of the panel and the bottom of the page or parent
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
    a number (interpreted as pixels) or a valid CSS size string, such as `"100px"`
    (100 pixels) or `"25%"`.

    For arcane HTML reasons, to have the panel fill the page or parent,
    specify 0 for ``top``, ``left``, ``right``, and ``bottom`` rather than the more
    obvious `width = "100%"` and `height = "100%"`.
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
    # Add Shiny inputs and htmlwidgets to 'non-draggable' elements
    # Cf. https://api.jqueryui.com/draggable/#option-cancel
    dragOpts = '{cancel: ".shiny-input-container,.html-widget,input,textarea,button,select,option"}'
    return TagList(deps, divTag, tags.script(f'$(".draggable").draggable({dragOpts});'))


@no_example()
def help_text(*args: TagChild | TagAttrs, **kwargs: TagAttrValue) -> Tag:
    """
    Create a help text element

    Help text is stylized text which can be added to the user interface to provide additional explanation
    or context. Text passed to :func:`~shiny.ui.help_text` receives the Bootstrap `help-block` class.

    Parameters
    ----------
    *args
        UI elements to include inside the help text.
    **kwargs
        Attributes to add to the text container.

    Returns
    -------
    :
        A UI element
    """

    return span({"class": "help-block"}, *args, **kwargs)
