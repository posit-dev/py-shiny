from typing import Optional, Union, List, Dict

from htmltools import tags, Tag, div, span, css, TagChildArg

from .input_utils import shiny_input_label


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


choicesType = Union[Dict[str, str], List[str]]


def input_checkbox_group(
    id: str,
    label: TagChildArg,
    choices: choicesType,
    choice_names: Optional[List[str]] = None,
    selected: Optional[str] = None,
    inline: bool = False,
    width: Optional[str] = None,
) -> Tag:
    input_label = shiny_input_label(id, label)
    options = generate_options(
        id=id,
        type="checkbox",
        choices=choices,
        choice_names=choice_names,
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


def input_radio_buttons(
    id: str,
    label: TagChildArg,
    choices: choicesType,
    choice_names: Optional[List[str]] = None,
    selected: Optional[str] = None,
    inline: bool = False,
    width: Optional[str] = None,
) -> Tag:
    input_label = shiny_input_label(id, label)
    options = generate_options(
        id=id,
        type="radio",
        choices=choices,
        choice_names=choice_names,
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


def generate_options(
    id: str,
    type: str,
    choices: choicesType,
    choice_names: Optional[List[str]],
    selected: Optional[str],
    inline: bool,
):
    if not choice_names:
        choice_names = list(choices.keys()) if isinstance(choices, dict) else choices
    choices = [v for k, v in choices.items()] if isinstance(choices, dict) else choices
    if type == "radio" and not selected:
        selected = choices[0]
    return div(
        *[
            generate_option(id, type, choices[i], choice_names[i], selected, inline)
            for i in range(len(choices))
        ],
        class_="shiny-options-group",
    )


def generate_option(
    id: str,
    type: str,
    choice: str,
    choice_name: str,
    selected: Optional[str],
    inline: bool,
):
    input = tags.input(
        type=type,
        name=id,
        value=choice,
        checked="checked" if selected == choice else None,
    )
    if inline:
        return tags.label(input, span(choice_name), class_=type + "-inline")
    else:
        return div(tags.label(input, span(choice_name)), class_=type)
