from htmltools import tags, Tag, div, css
from typing import Optional
from .input_utils import *


def passwordInput(
    id: str,
    label: str,
    value: str = "",
    width: Optional[str] = None,
    placeholder: Optional[str] = None,
) -> Tag:
    return div(
        shiny_input_label(id, label),
        tags.input(
            id=id,
            type="password",
            value=value,
            class_="form-control",
            placeholder=placeholder,
        ),
        class_="form-group shiny-input-container",
        style=css(width=width),
    )
