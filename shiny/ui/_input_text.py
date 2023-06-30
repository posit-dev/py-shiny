__all__ = ("input_text", "input_text_area")

from typing import Literal, Optional

from htmltools import Tag, TagChild, css, div, tags

from .._docstring import add_example
from .._namespaces import resolve_id
from ._utils import shiny_input_label


@add_example()
def input_text(
    id: str,
    label: TagChild,
    value: str = "",
    *,
    width: Optional[str] = None,
    placeholder: Optional[str] = None,
    autocomplete: Optional[str] = "off",
    spellcheck: Optional[Literal["true", "false"]] = None,
) -> Tag:
    """
    Create an input control for entry of text values

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
    autocomplete
        Whether to enable browser autocompletion of the text input (default is None).
        If None, then it will use the browser's default behavior. Other possible values
        include "on", "off", "name", "username", and "email". See
        https://developer.mozilla.org/en-US/docs/Web/HTML/Attributes/autocomplete for
        more.
    spellcheck
        Whether to enable browser spell checking of the text input (default is None). If
        None, then it will use the browser's default behavior.

    Returns
    -------
    :
        A UI element

    Notes
    ------
    ::: {.callout-note title="Server value"}
    A string containing the current text input. The default value is ``""`` unless
    ``value`` is provided.
    :::

    See Also
    -------
    ~shiny.ui.input_text_area
    """

    return div(
        shiny_input_label(id, label),
        tags.input(
            id=resolve_id(id),
            type="text",
            class_="form-control",
            value=value,
            placeholder=placeholder,
            autocomplete=autocomplete,
            spellcheck=spellcheck,
        ),
        class_="form-group shiny-input-container",
        style=css(width=width),
    )


@add_example()
def input_text_area(
    id: str,
    label: TagChild,
    value: str = "",
    *,
    width: Optional[str] = None,
    height: Optional[str] = None,
    cols: Optional[int] = None,
    rows: Optional[int] = None,
    placeholder: Optional[str] = None,
    resize: Optional[Literal["none", "both", "horizontal", "vertical"]] = None,
    autocomplete: Optional[str] = None,
    spellcheck: Optional[Literal["true", "false"]] = None,
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
    autocomplete
        Whether to enable browser autocompletion of the text input (default is "off").
        If None, then it will use the browser's default behavior. Other possible values
        include "on", "name", "username", and "email". See
        https://developer.mozilla.org/en-US/docs/Web/HTML/Attributes/autocomplete for
        more.
    spellcheck
        Whether to enable browser spell checking of the text input (default is None). If
        None, then it will use the browser's default behavior.

    Returns
    -------
    :
        A UI element

    Notes
    ------
    ::: {.callout-note title="Server value"}
    A string containing the current text input. The default value is ``""`` unless
    ``value`` is provided.
    :::

    See Also
    -------
    ~shiny.ui.input_text
    """

    if resize and resize not in ["none", "both", "horizontal", "vertical"]:
        raise ValueError("Invalid resize value: " + str(resize))

    area = tags.textarea(
        value,
        id=resolve_id(id),
        class_="form-control",
        style=css(width=None if width else "100%", height=height, resize=resize),
        placeholder=placeholder,
        rows=rows,
        cols=cols,
        autocomplete=autocomplete,
        spellcheck=spellcheck,
    )

    return div(
        shiny_input_label(id, label),
        area,
        class_="form-group shiny-input-container",
        style=css(width=width),
    )
