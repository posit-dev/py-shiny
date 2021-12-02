from typing import Optional, Dict, Any, Union, List, cast

from htmltools import Tag, TagAttrArg, JSXTag, jsx_tag_create, tags, div

from .html_dependencies import selectize_deps, jqui_deps
from .input_utils import shiny_input_label

# This is the canonical format for representing select options.
SelectInputOptions = Dict[str, Union[str, Dict[str, str]]]


def input_selectize(
    id: str, options: Dict[str, Any] = {}, **kwargs: TagAttrArg
) -> JSXTag:
    # Make sure accessibility plugin is included by default
    if not options.get("plugins", None):
        options["plugins"] = []
    if "selectize-plugin-a11y" not in options["plugins"]:
        options["plugins"].append("selectize-plugin-a11y")
    deps = [selectize_deps()]
    if "drag_drop" in options["plugins"]:
        deps.append(jqui_deps())
    return jsx_tag_create("InputSelectize")(deps, id=id, options=options, **kwargs)


def input_select(
    id: str,
    label: str,
    choices: Union[List[str], Dict[str, Union[str, List[str], Dict[str, str]]]],
    selected: Optional[str] = None,
    multiple: bool = False,
    selectize: bool = True,
    width: Optional[str] = None,
    size: Optional[str] = None,
) -> Tag:

    choices_ = _normalize_choices(choices)
    choices_tags = _render_choices(choices_, selected)

    return div(
        shiny_input_label(id, label),
        tags.select(
            *choices_tags,
            selectize_deps(),
            id=id,
            label=label,
            class_="form-select",
            multiple=multiple,
            width=width,
            size=size,
        ),
        class_="form-group shiny-input-container",
    )


def _normalize_choices(
    x: Union[List[str], Dict[str, Union[str, List[str], Dict[str, str]]]]
) -> SelectInputOptions:
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


def _render_choices(x: SelectInputOptions, selected: Optional[str] = None) -> List[Tag]:
    # TODO: if selected is None, select the first item.

    result: List[Tag] = []
    for (label, value) in x.items():
        if isinstance(value, dict):
            # Type checker needs a little help here -- value is already a narrower type
            # than SelectInputOptions.
            value = cast(SelectInputOptions, value)
            result.append(
                tags.optgroup(*(_render_choices(value, selected)), label=label)
            )
        else:
            result.append(tags.option(label, value=value, selected=(value == selected)))

    return result
