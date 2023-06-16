# Using sep file from `_bootstrap.py` to avoid circular imports
from __future__ import annotations

__all__ = (
    "row",
    "column",
)

from htmltools import Tag, TagAttrs, TagAttrValue, TagChild, div

from .._docstring import add_example


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
