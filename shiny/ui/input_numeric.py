__all__ = ("input_numeric",)

from typing import Optional

from htmltools import tags, Tag, div, css, TagChildArg

from .input_utils import shiny_input_label


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
