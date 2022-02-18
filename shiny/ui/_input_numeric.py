__all__ = ("input_numeric",)

from typing import Optional

from htmltools import tags, Tag, div, css, TagChildArg

from .._docstring import add_example
from ._utils import shiny_input_label


@add_example()
def input_numeric(
    id: str,
    label: TagChildArg,
    value: float,
    min: Optional[float] = None,
    max: Optional[float] = None,
    step: Optional[float] = None,
    width: Optional[str] = None,
) -> Tag:
    """
    Create an input control for entry of numeric values.

    Parameters
    ----------
    id
        An input id.
    label
        An input label.
    value
        Initial value.
    min
        The minimum allowed value.
    max
        The maximum allowed value.
    step
        Interval to use when stepping between min and max.
    width
        The CSS width, e.g. '400px', or '100%'

    Returns
    -------
    A UI element.

    Notes
    ------
    .. admonition:: Server value

        A numeric value.

    See Also
    -------
    ~shiny.ui.update_numeric
    """

    return div(
        shiny_input_label(id, label),
        tags.input(
            id=id,
            type="number",
            class_="form-control",
            value=value,
            min=min,
            max=max,
            step=step,
        ),
        class_="form-group shiny-input-container",
        style=css(width=width),
    )
