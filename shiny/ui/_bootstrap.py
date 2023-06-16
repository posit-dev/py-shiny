from __future__ import annotations

__all__ = (
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

from typing import Optional

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
from .._typing_extensions import Literal
from ..experimental.ui._sidebar import Sidebar as XSidebar
from ..experimental.ui._sidebar import layout_sidebar as x_layout_sidebar
from ..experimental.ui._sidebar import sidebar as x_sidebar
from ..experimental.ui._utils import consolidate_attrs as x_consolidate_attrs
from ..module import current_namespace
from ..types import MISSING, MISSING_TYPE
from ._html_dependencies import jqui_deps
from ._utils import get_window_title


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

    if not isinstance(sidebar, PanelSidebar):
        sidebar = PanelSidebar(sidebar)
    if not isinstance(main, PanelMain):
        main = PanelMain(attrs={}, children=[main])

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
    return PanelSidebar(*args, width=width, **kwargs)


class PanelSidebar:
    # Store `attrs` for `layout_sidebar()` to retrieve
    def __init__(
        self, *args: TagChild | TagAttrs, width: int = 4, **kwargs: TagAttrValue
    ) -> None:
        self.args = args
        self.kwargs = kwargs
        self.width = width

    def get_sidebar(self, position: Literal["left", "right"] = "left") -> XSidebar:
        return x_sidebar(
            *self.args,
            width=f"{int(self.width / 12 * 100)}%",
            position=position,
            open="always",
            **self.kwargs,
        )

    # Hopefully this is never used. But it makes it Tagifiable to allow us to not expose
    # `XSidebar` and `PanelSidebar` classes
    def tagify(self) -> Tag:
        return self.get_sidebar().tag.tagify()


def panel_main(
    *args: TagChild | TagAttrs,
    width: int = 8,
    **kwargs: TagAttrValue,
) -> Tagifiable:
    """
    Create an main area panel

    See :func:`~shiny.ui.layout_sidebar` for more information and an example.

    Parameters
    ----------
    args
        UI elements to include inside the main area.
    width
        The width of the main area (an integer between 1 and 12).
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
    if width != 8:
        warn_deprecated(
            "panel_main(width=)` is being ignored. Given the sidebar width, the main panel will take up the remaining horizontal space."
        )
    attrs, children = x_consolidate_attrs(*args, **kwargs)
    if len(attrs) > 0:
        return PanelMain(attrs=attrs, children=children)

    return TagList(*children)


class PanelMain:
    # Store `attrs` for `layout_sidebar()` to retrieve
    attrs: TagAttrs
    # Return `children` in `layout_sidebar()` via `.tagify()` method
    children: list[TagChild]

    def __init__(self, *, attrs: TagAttrs, children: list[TagChild]) -> None:
        self.attrs = attrs
        self.children = children

    def tagify(self) -> TagList:
        return TagList(self.children).tagify()


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
