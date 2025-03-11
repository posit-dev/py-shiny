__all__ = ("input_password",)

from typing import Literal, Optional

from htmltools import Tag, TagChild, css, div, tags

from .._docstring import add_example
from ..module import resolve_id
from ._utils import shiny_input_label


@add_example()
def input_password(
    id: str,
    label: TagChild,
    value: str = "",
    *,
    width: Optional[str] = None,
    placeholder: Optional[str] = None,
    update_on: Literal["change", "blur"] = "change",
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
        The CSS width, e.g., '400px', or '100%'.
    placeholder
        The placeholder of the input.
    update_on
        When should the input value be updated? Options are `"change"` (default) and
        `"blur"`. Use `"change"` to update the input immediately whenever the value
        changes. Use `"blur"`to delay the input update until the input loses focus (the
        user moves away from the input), or when Enter is pressed.

    Returns
    -------
    :
        A UI element.

    Notes
    ------
    ::: {.callout-note title="Server value"}
    A string of the password input. The default value is unless value is provided.
    :::

    See Also
    --------
    * :func:`~shiny.ui.update_text`
    """
    resolved_id = resolve_id(id)
    return div(
        shiny_input_label(resolved_id, label),
        tags.input(
            id=resolved_id,
            type="password",
            value=value,
            class_="shiny-input-password form-control",
            placeholder=placeholder,
            data_update_on=update_on,
        ),
        class_="form-group shiny-input-container",
        style=css(width=width),
    )
