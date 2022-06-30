__all__ = ("input_password",)

from typing import Optional

from htmltools import tags, Tag, div, css, TagChildArg

from .._docstring import add_example
from .._namespaces import resolve_id
from ._utils import shiny_input_label


@add_example()
def input_password(
    id: str,
    label: TagChildArg,
    value: str = "",
    *,
    width: Optional[str] = None,
    placeholder: Optional[str] = None,
) -> Tag:
    """
    Create an password control for entry of passwords.

    Parameters
    ----------
    id
        An input id.
    label
        An input label.
    value
        Initial value.
    width
        The CSS width, e.g. '400px', or '100%'
    placeholder
        The placeholder of the input.

    Returns
    -------
    A UI element.

    Notes
    ------
    .. admonition:: Server value

        A string of the password input. The default value is unless value is provided.

    See Also
    -------
    ~shiny.ui.update_text
    """
    return div(
        shiny_input_label(id, label),
        tags.input(
            id=resolve_id(id),
            type="password",
            value=value,
            class_="form-control",
            placeholder=placeholder,
        ),
        class_="form-group shiny-input-container",
        style=css(width=width),
    )
