from typing import Optional, Dict, Union, List, cast

from htmltools import Tag, tags, div, TagChildArg

from .html_dependencies import selectize_deps
from .input_utils import shiny_input_label

# This is the canonical format for representing select options.
SelectChoicesArg = Union[List[str], Dict[str, Union[str, List[str], Dict[str, str]]]]
_SelectChoices = Dict[str, Union[str, Dict[str, str]]]


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
    # # Make sure accessibility plugin is included by default
    # if not options.get("plugins", None):
    #     options["plugins"] = []
    # if "selectize-plugin-a11y" not in options["plugins"]:
    #     options["plugins"].append("selectize-plugin-a11y")
    # deps = [selectize_deps()]
    # if "drag_drop" in options["plugins"]:
    #     deps.append(jqui_deps())
    # return jsx_tag_create("InputSelectize")(deps, id=id, options=options, **kwargs)


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
                [
                    tags.script("{}", type="application/json", data_for=id),
                    selectize_deps(),
                ]
                if selectize
                else None
            ),
        ),
        class_="form-group shiny-input-container",
    )


# x can be structured like any of the following:
# List:
#   ["a", "b", "c"]
# Dictionary:
#   {"Choice A": "a", "Choice B": "b", "Choice C": "c"}
# Dictionary with sub-lists or sub-dictionaries (which are optgroups):
#   {
#     "Choice A": "a",
#     "Group B": {"Choice B1": "b1", "Choice B2": "b2"},
#     "Group C: ["c1, "c2"]
#   }
def _normalize_choices(
    x: Union[List[str], Dict[str, Union[str, List[str], Dict[str, str]]]]
) -> _SelectChoices:
    if isinstance(x, list):
        return {k: k for k in x}

    # If we got here, it's a dict. The value of each item.
    result = x.copy()
    for (k, value) in result.items():
        # Convert list[str] to dict[str, str], but leave str, and dict[str, str] alone.
        if isinstance(value, list):
            result[k] = {k: k for k in value}

    # The type checker isn't smart enough to realize that none of the values are lists
    # at this point, so tell it to ignore the type.
    return result  # type: ignore


def _render_choices(x: _SelectChoices, selected: Optional[str] = None) -> List[Tag]:
    result: List[Tag] = []
    for (label, value) in x.items():
        if isinstance(value, dict):
            # Type checker needs a little help here -- value is already a narrower type
            # than _SelectChoices.
            value = cast(_SelectChoices, value)
            result.append(
                tags.optgroup(*(_render_choices(value, selected)), label=label)
            )
        else:
            result.append(tags.option(label, value=value, selected=(value == selected)))

    return result


# Returns the first option in a _SelectChoices object. For most cases, this is
# straightforward. In the following, the first option is "a":
# { "Choice A": "a", "Choice B": "b", "Choice C": "c" }
#
# Sometimes the first option is nested within an optgroup. For example, in the
# following, the first option is "b1":
# {
#     "Group A": {},
#     "Group B": {"Choice B1": "b1", "Choice B2": "b2"},
# }
def _find_first_option(x: _SelectChoices) -> Optional[str]:
    for (_label, value) in x.items():
        if isinstance(value, dict):
            value = cast(_SelectChoices, value)
            result = _find_first_option(value)
            if result is not None:
                return result
        else:
            return value

    return None
