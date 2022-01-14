from typing import Optional, Sequence, Union, List, Tuple

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


CheckChoicesArg = Union[Sequence[str], Sequence[Tuple[str, str]]]


def input_checkbox_group(
    id: str,
    label: TagChildArg,
    choices: CheckChoicesArg,
    selected: Optional[str] = None,
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


def input_radio_buttons(
    id: str,
    label: TagChildArg,
    choices: CheckChoicesArg,
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
    choices: CheckChoicesArg,
    selected: Optional[str],
    inline: bool,
):
    choicez = _standardize_choices(choices)
    if type == "radio" and not selected:
        selected = choicez[0][1]
    return div(
        *[_generate_option(id, type, choice, selected, inline) for choice in choicez],
        class_="shiny-options-group",
    )


def _generate_option(
    id: str,
    type: str,
    choice: Tuple[str, str],
    selected: Optional[str],
    inline: bool,
):
    input = tags.input(
        type=type,
        name=id,
        value=choice[1],
        checked="checked" if selected == choice[1] else None,
    )
    if inline:
        return tags.label(input, span(choice[0]), class_=type + "-inline")
    else:
        return div(tags.label(input, span(choice[0])), class_=type)


def _standardize_choices(x: CheckChoicesArg) -> Sequence[Tuple[str, str]]:
    res: List[Tuple[str, str]] = []
    for choice in x:
        # TODO: maybe this should use TypeGuard? https://docs.python.org/3/library/typing.html#typing.TypeGuard
        if isinstance(choice, str):
            res.append((choice, choice))
        elif len(choice) == 2:
            res.append(choice)
        else:
            raise ValueError("`choices` must be a list of strings or tuples of strings")
    return tuple(res)
