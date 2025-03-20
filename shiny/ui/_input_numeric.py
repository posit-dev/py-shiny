__all__ = ("input_numeric",)

from typing import Literal, Optional

from htmltools import Tag, TagChild, css, div, tags

from .._docstring import add_example
from ..bookmark import restore_input
from ..module import resolve_id
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
    update_on: Literal["change", "blur"] = "change",
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
    update_on
        When should the input value be updated? Options are `"change"` (default) and
        `"blur"`. Use `"change"` to update the input immediately whenever the value
        changes. Use `"blur"`to delay the input update until the input loses focus (the
        user moves away from the input), or when Enter is pressed.

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
    --------
    * :func:`~shiny.ui.update_numeric`
    """

    resolved_id = resolve_id(id)
    return div(
        shiny_input_label(resolved_id, label),
        tags.input(
            id=resolved_id,
            type="number",
            class_="shiny-input-number form-control",
            value=restore_input(resolved_id, value),
            min=min,
            max=max,
            step=step,
            data_update_on=update_on,
        ),
        class_="form-group shiny-input-container",
        style=css(width=width),
    )
