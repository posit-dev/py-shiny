from htmltools import tags, Tag, div, css, TagChildArg
from typing import Optional, Union
from .input_utils import shiny_input_label

valType = Union[int, float]


def input_numeric(
    id: str,
    label: TagChildArg,
    value: valType,
    min: Optional[valType] = None,
    max: Optional[valType] = None,
    step: Optional[valType] = None,
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
