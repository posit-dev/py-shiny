__all__ = ("input_numeric",)

from typing import Optional

from htmltools import tags, Tag, div, css, TagChildArg

from .._docstring import doc
from ._utils import shiny_input_label


@doc(
    "Create an input control for entry of numeric values.",
    returns="A UI element.",
    topics={"Server value": "A numeric value."},
    see_also=[
        ":func:`~shiny.ui.update_numeric`",
    ],
)
def input_numeric(
    id: str,
    label: TagChildArg,
    value: float,
    min: Optional[float] = None,
    max: Optional[float] = None,
    step: Optional[float] = None,
    width: Optional[str] = None,
) -> Tag:
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
