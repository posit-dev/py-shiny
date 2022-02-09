__all__ = (
    "input_select",
    "input_selectize",
)

from typing import Optional, Dict, Union, List

from htmltools import Tag, tags, div, TagChildArg, TagList

from ._html_dependencies import selectize_deps
from ._input_utils import shiny_input_label

_Choices = Dict[str, TagChildArg]
_OptGrpChoices = Dict[str, _Choices]

# Canonical format for representing select options.
_SelectChoices = Union[_Choices, _OptGrpChoices]

# Formats available to the user
SelectChoicesArg = Union[
    # ["a", "b", "c"]
    List[str],
    # {"a": "Choice A", "b": tags.i("Choice B")}
    _Choices,
    # optgroup {"Group A": {"a1": "Choice A1", "a2": tags.i("Choice A2")}, "Group B": {}}
    _OptGrpChoices,
]


def input_selectize(
    id: str,
    label: TagChildArg,
    choices: SelectChoicesArg,
    *,
    selected: Optional[str] = None,
    multiple: bool = False,
    width: Optional[str] = None,
    size: Optional[str] = None,
) -> Tag:

    return input_select(
        id,
        label,
        choices,
        selected=selected,
        multiple=multiple,
        selectize=True,
        width=width,
        size=size,
    )


def input_select(
    id: str,
    label: TagChildArg,
    choices: SelectChoicesArg,
    *,
    selected: Optional[str] = None,
    multiple: bool = False,
    selectize: bool = False,
    width: Optional[str] = None,
    size: Optional[str] = None,
) -> Tag:

    choices_ = _normalize_choices(choices)
    if selected is None:
        selected = _find_first_option(choices_)

    choices_tags = _render_choices(choices_, selected)

    return div(
        shiny_input_label(id, label),
        div(
            tags.select(
                *choices_tags,
                id=id,
                class_=None if selectize else "form-select",
                multiple=multiple,
                width=width,
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
    )


def _normalize_choices(x: SelectChoicesArg) -> _SelectChoices:
    if isinstance(x, list):
        return {k: k for k in x}
    else:
        return x


def _render_choices(x: _SelectChoices, selected: Optional[str] = None) -> List[Tag]:
    result: List[Tag] = []
    for (k, v) in x.items():
        if isinstance(v, dict):
            result.append(tags.optgroup(*(_render_choices(v, selected)), label=k))
        else:
            result.append(tags.option(v, value=k, selected=(k == selected)))

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
    for (k, v) in x.items():
        if isinstance(v, dict):
            result = _find_first_option(v)
            if result is not None:
                return result
        else:
            return k

    return None
