__all__ = (
    "input_checkbox",
    "input_checkbox_group",
    "input_radio_buttons",
)

from typing import Optional, Dict, Union, List, Tuple

from htmltools import tags, Tag, div, span, css, TagChildArg


from .._docstring import doc
from ._utils import shiny_input_label

# Canonical format for representing select options.
_Choices = Dict[str, TagChildArg]

# Formats available to the user
ChoicesArg = Union[List[str], _Choices]


@doc(
    "Create a checkbox that can be used to specify logical values.",
    returns="A UI element.",
    topics={"Server value": "True if checked, False otherwise."},
    see_also=[
        ":func:`~shiny.ui.update_checkbox`",
        ":func:`~shiny.ui.input_checkbox_group`",
        ":func:`~shiny.ui.input_radio_buttons`",
    ],
)
def input_checkbox(
    id: str, label: TagChildArg, value: bool = False, width: Optional[str] = None
) -> Tag:
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


@doc(
    """
    Create a group of checkboxes that can be used to toggle multiple choices
    independently. The server will receive the input as a character vector of the
    selected values.
    """,
    returns="A UI element.",
    topics={"Server value": "A list of string(s) with the selected value(s) (if any)."},
    see_also=[
        ":func:`~shiny.ui.update_checkbox_group",
        ":func:`~shiny.ui.input_checkbox",
        ":func:`~shiny.ui.input_radio_buttons",
    ],
)
def input_checkbox_group(
    id: str,
    label: TagChildArg,
    choices: ChoicesArg,
    selected: Optional[Union[str, List[str]]] = None,
    inline: bool = False,
    width: Optional[str] = None,
) -> Tag:
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


@doc(
    "Create a set of radio buttons used to select an item from a list.",
    returns="A UI element",
    topics={"Server value": "A string with the selected value."},
    see_also=[
        ":func:`~shiny.ui.update_radio_buttons",
        ":func:`~shiny.ui.input_checkbox_group",
        ":func:`~shiny.ui.input_checkbox",
    ],
)
def input_radio_buttons(
    id: str,
    label: TagChildArg,
    choices: ChoicesArg,
    selected: Optional[str] = None,
    inline: bool = False,
    width: Optional[str] = None,
) -> Tag:
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
