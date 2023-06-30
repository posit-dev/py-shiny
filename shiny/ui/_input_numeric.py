__all__ = ("input_numeric",)

from typing import Optional

from htmltools import Tag, TagChild, css, div, tags

from .._docstring import add_example
from .._namespaces import resolve_id
from ._utils import shiny_input_label


@add_example()
def input_numeric(
    id: str,
    label: TagChild,
    value: float,
    *,
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
    :
        A UI element.

    Notes
    ------
    ::: {.callout-note title="Server value"}
    A numeric value.
    :::

    See Also
    -------
    ~shiny.ui.update_numeric
    """

    return div(
        shiny_input_label(id, label),
        tags.input(
            id=resolve_id(id),
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
