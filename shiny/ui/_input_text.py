__all__ = ("input_text", "input_text_area")

from typing import Optional

from htmltools import tags, Tag, div, css, TagChildArg

from .._docstring import add_example
from ._utils import shiny_input_label


@add_example()
def input_text(
    id: str,
    label: TagChildArg,
    value: str = "",
    width: Optional[str] = None,
    placeholder: Optional[str] = None,
) -> Tag:
    """
    Create an input control for entry of unstructured text values

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
        A hint as to what can be entered into the control.

    Returns
    -------
    A UI element

    Notes
    ------
    .. admonition:: Server value

        A string containing the current text input. The default value is ``""`` unless ``value`` is
    provided.

    See Also
    -------
    ~shiny.ui.input_text_area
    """

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


@add_example()
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
    """
    Create a textarea input control for entry of unstructured text values.

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
    height
        The CSS height, e.g. '400px', or '100%'
    cols
        Value of the visible character columns of the input, e.g. 80. This argument will
        only take effect if there is not a CSS width rule defined for this element; such
        a rule could come from the width argument of this function or from a containing
        page layout such as :func:`~shiny.ui.page_fluid`.
    rows
        The value of the visible character rows of the input, e.g. 6. If the height
        argument is specified, height will take precedence in the browser's rendering.
    placeholder
        A hint as to what can be entered into the control.
    resize
        Which directions the textarea box can be resized. Can be one of "both", "none",
        "vertical", and "horizontal". The default, ``None``, will use the client
        browser's default setting for resizing textareas.

    Returns
    -------
    A UI element

    Notes
    ------
    .. admonition:: Server value

        A string containing the current text input. The default value is ``""`` unless
        ``value`` is provided.

    See Also
    -------
    ~shiny.ui.input_text
    """

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
