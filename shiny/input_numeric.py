from htmltools import tags, div, css
from .input_utils import *
from typing import Optional, Union

valType = Union[int, float]


def numericInput(
    id: str,
    label: str,
    value: valType,
    min: Optional[valType] = None,
    max: Optional[valType] = None,
    step: Optional[valType] = None,
    width: Optional[str] = None,
):
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
