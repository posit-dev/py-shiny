__all__ = ("input_password",)

from typing import Optional

from htmltools import tags, Tag, div, css, TagChildArg

from .._docstring import doc
from ._utils import shiny_input_label


@doc(
    """
    Create an password control for entry of passwords.
    """,
    returns="A UI element.",
    topics={
        "Server value": """
A character string of the password input. The default value is unless value is provided.
"""
    },
    see_also=[
        ":func:`~shiny.ui.update_text`",
    ],
)
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
