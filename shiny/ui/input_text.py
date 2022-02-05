from typing import Optional

from htmltools import tags, Tag, div, css, TagChildArg

from .input_utils import shiny_input_label


def input_text(
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
            type="text",
            class_="form-control",
            value=value,
            placeholder=placeholder,
        ),
        class_="form-group shiny-input-container",
        style=css(width=width),
    )


def input_text_area(
    id: str,
    label: TagChildArg,
    value: str = "",
    width: Optional[str] = None,
    height: Optional[str] = None,
    cols: Optional[int] = None,
    rows: Optional[int] = None,
    placeholder: Optional[str] = None,
    resize: Optional[str] = None,
) -> Tag:

    if resize and resize not in ["none", "both", "horizontal", "vertical"]:
        raise ValueError("Invalid resize value: " + str(resize))

    area = tags.textarea(
        value,
        id=id,
        class_="form-control",
        style=css(width=None if width else "100%", height=height, resize=resize),
        placeholder=placeholder,
        rows=rows,
        cols=cols,
    )

    return div(
        shiny_input_label(id, label),
        area,
        class_="form-group shiny-input-container",
        style=css(width=width),
    )
