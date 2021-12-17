from htmltools import tags, Tag, div, span, css, TagChildArg
from typing import Optional, List
from .input_utils import shiny_input_label


def input_file(
    id: str,
    label: TagChildArg,
    multiple: bool = False,
    accept: Optional[List[str]] = None,
    width: Optional[str] = None,
    button_label: str = "Browse...",
    placeholder: str = "No file selected",
) -> Tag:
    btn_file = span(
        button_label,
        tags.input(
            id=id,
            name=id,
            type="file",
            multiple="multiple" if multiple else None,
            accept=",".join(accept) if accept else None,
            # Don't use "display: none;" style, which causes keyboard accessibility issue; instead use the following workaround: https://css-tricks.com/places-its-tempting-to-use-display-none-but-dont/
            style="position: absolute !important; top: -99999px !important; left: -99999px !important;",
        ),
        class_="btn btn-default btn-file",
    )
    return div(
        shiny_input_label(id, label),
        div(
            tags.label(btn_file, class_="input-group-btn input-group-prepend"),
            tags.input(
                type="text",
                class_="form-control",
                placeholder=placeholder,
                readonly="readonly",
            ),
            class_="input-group",
        ),
        div(
            div(class_="progress-bar"),
            id=id + "_progress",
            class_="progress active shiny-file-input-progress",
        ),
        class_="form-group shiny-input-container",
        style=css(width=width),
    )
