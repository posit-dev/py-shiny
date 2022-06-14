__all__ = (
    "input_checkbox",
    "input_checkbox_group",
    "input_radio_buttons",
)

from typing import Optional, Dict, Union, List, Tuple

from htmltools import tags, Tag, div, span, css, TagChildArg


from .._docstring import add_example
from ._utils import shiny_input_label

# Canonical format for representing select options.
_Choices = Dict[str, TagChildArg]

# Formats available to the user
ChoicesArg = Union[List[str], _Choices]


@add_example()
def input_checkbox(
    id: str, label: TagChildArg, value: bool = False, width: Optional[str] = None
) -> Tag:
    """
    Create a checkbox that can be used to specify logical values.

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

    Returns
    -------
    A UI element.

    Notes
    ------
    .. admonition:: Server value

        ``True`` if checked, ``False`` otherwise.

    See Also
    -------
    ~shiny.ui.update_checkbox
    ~shiny.ui.input_checkbox_group
    ~shiny.ui.input_radio_buttons
    """

    return div(
        div(
            tags.label(
                tags.input(
                    id=id, type="checkbox", checked="checked" if value else None
                ),
                span(label),
            ),
            class_="checkbox",
        ),
        class_="form-group shiny-input-container",
        style=css(width=width),
    )


@add_example()
def input_checkbox_group(
    id: str,
    label: TagChildArg,
    choices: ChoicesArg,
    selected: Optional[Union[str, List[str]]] = None,
    inline: bool = False,
    width: Optional[str] = None,
) -> Tag:
    """
    Create a group of checkboxes that can be used to toggle multiple choices
    independently.

    Parameters
    ----------
    id
        An input id.
    label
        An input label.
    choices
        Either a list of choices or a dictionary mapping choice values to labels. Note
        that if a dictionary is provided, the keys are used as the (input) values so
        that the dictionary values can hold HTML labels.
    selected
        The values that should be initially selected, if any.
    inline
        If `True`, the result is displayed inline
    width
        The CSS width, e.g. '400px', or '100%'

    Returns
    -------
    A UI element.

    Notes
    ------
    .. admonition:: Server value

        A tuple of string(s) with the selected value(s) (if any).

    See Also
    -------
    ~shiny.ui.update_checkbox_group
    ~shiny.ui.input_checkbox
    ~shiny.ui.input_radio_buttons
    """

    input_label = shiny_input_label(id, label)
    options = _generate_options(
        id=id,
        type="checkbox",
        choices=choices,
        selected=selected,
        inline=inline,
    )
    return div(
        input_label,
        options,
        id=id,
        style=css(width=width),
        class_="form-group shiny-input-checkboxgroup shiny-input-container"
        + (" shiny-input-container-inline" if inline else ""),
        # https://www.w3.org/TR/wai-aria-practices/examples/checkbox/checkbox-1/checkbox-1.html
        role="group",
        aria_labelledby=input_label.attrs.get("id"),
    )


@add_example()
def input_radio_buttons(
    id: str,
    label: TagChildArg,
    choices: ChoicesArg,
    selected: Optional[str] = None,
    inline: bool = False,
    width: Optional[str] = None,
) -> Tag:
    """
    Create a set of radio buttons used to select an item from a list.

    Parameters
    ----------
    id
        An input id.
    label
        An input label.
    choices
        Either a list of choices or a dictionary mapping choice values to labels. Note
        that if a dictionary is provided, the keys are used as the (input) values so
        that the dictionary values can hold HTML labels.
    selected
        The values that should be initially selected, if any.
    inline
        If ``True``, the result is displayed inline
    width
        The CSS width, e.g. '400px', or '100%'
    Returns
    -------
    A UI element

    Notes
    ------
    .. admonition:: Server value

        A string with the selected value.

    See Also
    -------
    ~shiny.ui.update_radio_buttons
    ~shiny.ui.input_checkbox_group
    ~shiny.ui.input_checkbox
    """

    input_label = shiny_input_label(id, label)
    options = _generate_options(
        id=id,
        type="radio",
        choices=choices,
        selected=selected,
        inline=inline,
    )
    return div(
        input_label,
        options,
        id=id,
        style=css(width=width),
        class_="form-group shiny-input-radiogroup shiny-input-container"
        + (" shiny-input-container-inline" if inline else ""),
        # https://www.w3.org/TR/2017/WD-wai-aria-practices-1.1-20170628/examples/radio/radio-1/radio-1.html
        role="radiogroup",
        aria_labelledby=input_label.attrs.get("id"),
    )


def _generate_options(
    id: str,
    type: str,
    choices: ChoicesArg,
    selected: Optional[Union[str, List[str]]],
    inline: bool,
):
    choicez = _normalize_choices(choices)
    if type == "radio" and not selected:
        selected = list(choicez.keys())[0]
    return div(
        *[
            _generate_option(id, type, choice, selected, inline)
            for choice in choicez.items()
        ],
        class_="shiny-options-group",
    )


def _generate_option(
    id: str,
    type: str,
    choice: Tuple[str, TagChildArg],
    selected: Optional[Union[str, List[str]]],
    inline: bool,
):
    value, label = choice
    if isinstance(selected, list):
        checked = value in selected
    else:
        checked = value == selected
    input = tags.input(
        type=type,
        name=id,
        value=value,
        checked="checked" if checked else None,
    )
    if inline:
        return tags.label(input, span(label), class_=type + "-inline")
    else:
        return div(tags.label(input, span(label)), class_=type)


def _normalize_choices(x: ChoicesArg) -> _Choices:
    if isinstance(x, list):
        return {k: k for k in x}
    else:
        return x
