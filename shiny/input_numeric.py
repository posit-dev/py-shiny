from typing import Optional, Union

from htmltools import tags, Tag, div, css, TagChildArg

from .input_utils import shiny_input_label

NumericValueArg = Union[int, float]


def input_numeric(
    id: str,
    label: TagChildArg,
    value: NumericValueArg,
    min: Optional[NumericValueArg] = None,
    max: Optional[NumericValueArg] = None,
    step: Optional[NumericValueArg] = None,
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
