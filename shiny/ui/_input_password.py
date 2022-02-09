__all__ = ("input_password",)

from typing import Optional

from htmltools import tags, Tag, div, css, TagChildArg

from ._input_utils import shiny_input_label


def input_password(
    id: str,
    label: TagChildArg,
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
