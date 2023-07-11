# pyright: reportUnnecessaryComparison=false

from __future__ import annotations

__all__ = (
    "input_select",
    "input_selectize",
)

from typing import Mapping, Optional, Union, cast

from htmltools import Tag, TagChild, TagList, css, div, tags

from .._docstring import add_example
from .._namespaces import resolve_id
from ._html_dependencies import selectize_deps
from ._utils import shiny_input_label

_Choices = Mapping[str, TagChild]
_OptGrpChoices = Mapping[str, _Choices]

# Canonical format for representing select options.
_SelectChoices = Union[_Choices, _OptGrpChoices]

# Formats available to the user
SelectChoicesArg = Union[
    # ["a", "b", "c"]
    "list[str]",
    # ("a", "b", "c")
    "tuple[str, ...]",
    # {"a": "Choice A", "b": tags.i("Choice B")}
    _Choices,
    # optgroup {"Group A": {"a1": "Choice A1", "a2": tags.i("Choice A2")}, "Group B": {}}
    _OptGrpChoices,
]


_topics = {
    "Server value": """
A list of strings, usually of length 1, with the value of the selected items. When
``multiple=True`` and nothing is selected, this value will be ``None``.
"""
}


@add_example()
def input_selectize(
    id: str,
    label: TagChild,
    choices: SelectChoicesArg,
    *,
    selected: Optional[str | list[str]] = None,
    multiple: bool = False,
    width: Optional[str] = None,
) -> Tag:
    """
    Create a select list that can be used to choose a single or multiple items from a
    list of values.

    Parameters
    ----------
    id
        An input id.
    label
        An input label.
    choices
        Either a list of choices or a dictionary mapping choice values to labels. Note
        that if a dictionary is provided, the keys are used as the (input) values so
        that the dictionary values can hold HTML labels. A dictionary of dictionaries is
        also supported, and in that case, the top-level keys are treated as
        ``<optgroup>`` labels.
    selected
        The values that should be initially selected, if any.
    multiple
        Is selection of multiple items allowed?
    width
        The CSS width, e.g. '400px', or '100%'

    Returns
    -------
    :
        A UI element.

    Notes
    ------
    ::: {.callout-note title="Server value"}
    A list of strings, usually of length 1, with the value of the selected items. When
    ``multiple=True`` and nothing is selected, this value will be ``None``.
    :::

    See Also
    -------
    ~shiny.ui.input_select ~shiny.ui.input_radio_buttons ~shiny.ui.input_checkbox_group
    """

    return input_select(
        id,
        label,
        choices,
        selected=selected,
        multiple=multiple,
        selectize=True,
        width=width,
    )


@add_example()
def input_select(
    id: str,
    label: TagChild,
    choices: SelectChoicesArg,
    *,
    selected: Optional[str | list[str]] = None,
    multiple: bool = False,
    selectize: bool = False,
    width: Optional[str] = None,
    size: Optional[str] = None,
) -> Tag:
    """
    Create a select list that can be used to choose a single or multiple items from a
    list of values.

    Parameters
    ----------
    id
        An input id.
    label
        An input label.
    choices
        Either a list of choices or a dictionary mapping choice values to labels. Note
        that if a dictionary is provided, the keys are used as the (input) values so
        that the dictionary values can hold HTML labels. A dictionary of dictionaries is
        also supported, and in that case, the top-level keys are treated as
        ``<optgroup>`` labels.
    selected
        The values that should be initially selected, if any.
    multiple
        Is selection of multiple items allowed?
    selectize
        Whether to use selectize.js or not.
    width
        The CSS width, e.g. '400px', or '100%'
    size
        Number of items to show in the selection box; a larger number will result in a
        taller box. Normally, when ``multiple=False``, a select input will be a
        drop-down list, but when size is set, it will be a box instead.

    Returns
    -------
    :
        A UI element.

    Notes
    ------
    ::: {.callout-note title="Server value"}
    A list of strings, usually of length 1, with the value of the selected items. When
    ``multiple=True`` and nothing is selected, this value will be ``None``.
    :::

    See Also
    -------
    ~shiny.ui.input_selectize
    ~shiny.ui.update_select
    ~shiny.ui.input_radio_buttons
    ~shiny.ui.input_checkbox_group
    """

    choices_ = _normalize_choices(choices)
    if selected is None and not multiple:
        selected = _find_first_option(choices_)

    choices_tags = _render_choices(choices_, selected)

    id = resolve_id(id)

    return div(
        shiny_input_label(id, label),
        div(
            tags.select(
                *choices_tags,
                id=id,
                class_=None if selectize else "form-select",
                multiple=multiple,
                size=size,
            ),
            (
                TagList(
                    tags.script("{}", type="application/json", data_for=id),
                    selectize_deps(),
                )
                if selectize
                else None
            ),
        ),
        class_="form-group shiny-input-container",
        style=css(width=width),
    )


def _normalize_choices(x: SelectChoicesArg) -> _SelectChoices:
    if x is None:
        raise TypeError("`choices` must be a list, tuple, or dict.")
    elif isinstance(x, (list, tuple)):
        return {k: k for k in x}
    else:
        return x


def _render_choices(
    x: _SelectChoices, selected: Optional[str | list[str]] = None
) -> TagList:
    result = TagList()

    if x is None:
        return result

    for k, v in x.items():
        if isinstance(v, Mapping):
            result.append(
                tags.optgroup(
                    *(_render_choices(cast(_SelectChoices, v), selected)), label=k
                )
            )
        else:
            is_selected = False
            if isinstance(selected, list):
                is_selected = k in selected
            else:
                is_selected = k == selected

            result.append(tags.option(v, value=k, selected=is_selected))

    return result


# Returns the first option in a _SelectChoices object. For most cases, this is
# straightforward. In the following, the first option is "a":
# {"a": "Choice A", "b": "Choice B", "c": "Choice C"}
#
# Sometimes the first option is nested within an optgroup. For example, in the
# following, the first option is "b1":
# {
#     "Group A": {},
#     "Group B": {"Choice B1": "b1", "Choice B2": "b2"},
# }
def _find_first_option(x: _SelectChoices) -> Optional[str]:
    if x is None:
        return None

    for k, v in x.items():
        if isinstance(v, dict):
            result = _find_first_option(cast(_SelectChoices, v))
            if result is not None:
                return result
        else:
            return k

    return None
