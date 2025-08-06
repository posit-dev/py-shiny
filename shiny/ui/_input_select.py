# pyright: reportUnnecessaryComparison=false

from __future__ import annotations

from .._deprecated import warn_deprecated
from ..types import DEPRECATED, MISSING_TYPE, Jsonifiable

__all__ = (
    "input_select",
    "input_selectize",
)
import copy
from json import dumps
from typing import Any, Mapping, Optional, Union, cast

from htmltools import Tag, TagChild, TagList, css, div, tags

from .._docstring import add_example
from ..bookmark import restore_input
from ..module import resolve_id
from ._html_deps_external import selectize_deps
from ._utils import JSEval, extract_js_keys, shiny_input_label

_Choices = Mapping[str, str]
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
If `multiple=False`, the server value is a string with the value of the selected item.
If `multiple=True`, the server value is a tuple containing the values of the
selected items. When ``multiple=True`` and nothing is selected, this value
will be ``None``.
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
    remove_button: Optional[bool] = None,
    options: Optional[dict[str, Jsonifiable | JSEval]] = None,
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
        that if a dictionary is provided, the keys are used as the (input) values and
        the values are labels displayed to the user. A dictionary of dictionaries is
        also supported, and in that case, the top-level keys are treated as
        ``<optgroup>`` labels.
    selected
        The values that should be initially selected, if any.
    multiple
        Is selection of multiple items allowed?
    width
        The CSS width, e.g. '400px', or '100%'
    remove_button
        Whether to add a remove button. This uses the `clear_button` and `remove_button`
        selectize plugins which can also be supplied as options. By default it will apply a
        remove button to multiple selections, but not single selections.
    options
        A dictionary of options. See the documentation of selectize.js for possible options.
        If you want to pass a JavaScript function, wrap the string in `ui.JS`.

    Returns
    -------
    :
        A UI element.

    Notes
    ------
    ::: {.callout-note title="Server value"}
    If `multiple=False`, the server value is a string with the value of the selected item.
    If `multiple=True`, the server value is a tuple containing the values of the
    selected items. When ``multiple=True`` and nothing is selected, this value
    will be ``None``.
    :::

    See Also
    --------
    * :func:`~shiny.ui.input_select`
    * :func:`~shiny.ui.input_radio_buttons`
    * :func:`~shiny.ui.input_checkbox_group`
    """
    resolved_id = resolve_id(id)

    x = _input_select_impl(
        id=resolved_id,
        label=label,
        choices=restore_input(resolved_id, choices),
        selected=selected,
        multiple=multiple,
        selectize=True,
        width=width,
        remove_button=remove_button,
        options=options,
    )

    return x


@add_example()
def input_select(
    id: str,
    label: TagChild,
    choices: SelectChoicesArg,
    *,
    selected: Optional[str | list[str]] = None,
    multiple: bool = False,
    selectize: bool | MISSING_TYPE = DEPRECATED,
    width: Optional[str] = None,
    size: Optional[str] = None,
    remove_button: Optional[bool] | MISSING_TYPE = DEPRECATED,
    options: Optional[dict[str, Jsonifiable | JSEval]] | MISSING_TYPE = DEPRECATED,
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
        that if a dictionary is provided, the keys are used as the (input) values and
        the values are labels displayed to the user. A dictionary of dictionaries is
        also supported, and in that case, the top-level keys are treated as
        ``<optgroup>`` labels.
    selected
        The values that should be initially selected, if any.
    multiple
        Is selection of multiple items allowed?
    selectize
        Deprecated. Use ``input_selectize()`` instead of passing ``selectize=True``.
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
    If `multiple=False`, the server value is a string with the value of the selected item.
    If `multiple=True`, the server value is a tuple containing the values of the
    selected items. When ``multiple=True`` and nothing is selected, this value
    will be ``None``.
    :::

    See Also
    --------
    * :func:`~shiny.ui.input_selectize`
    * :func:`~shiny.ui.update_select`
    * :func:`~shiny.ui.input_radio_buttons`
    * :func:`~shiny.ui.input_checkbox_group`
    """
    if isinstance(selectize, MISSING_TYPE):
        selectize = False
    else:
        warn_deprecated(
            "`selectize` parameter of `input_select()` is deprecated. "
            "Use `input_selectize()` instead of passing `selectize=True`."
        )

    if isinstance(remove_button, MISSING_TYPE):
        remove_button = None
    else:
        warn_deprecated(
            "`remove_button` parameter of `input_select()` is deprecated. "
            "Use `input_selectize()` instead."
        )

    if isinstance(options, MISSING_TYPE):
        options = None
    else:
        warn_deprecated(
            "`options` parameter of `input_select()` is deprecated. "
            "Use `input_selectize()` instead."
        )

    resolved_id = resolve_id(id)

    x = _input_select_impl(
        id=resolved_id,
        label=label,
        choices=choices,
        selected=selected,
        multiple=multiple,
        selectize=selectize,
        width=width,
        size=size,
        remove_button=remove_button,
        options=options,
    )

    return x


def _input_select_impl(
    id: str,
    label: TagChild,
    choices: SelectChoicesArg,
    *,
    selected: Optional[str | list[str]] = None,
    multiple: bool = False,
    selectize: bool = False,
    width: Optional[str] = None,
    size: Optional[str] = None,
    remove_button: Optional[bool] = None,
    options: Optional[dict[str, Jsonifiable | JSEval]] = None,
) -> Tag:
    if options is not None and selectize is False:
        raise Exception("Options can only be set when selectize is `True`.")

    remove_button = _resolve_remove_button(remove_button, multiple)

    resolved_id = resolve_id(id)

    choices_ = _normalize_choices(choices)

    selected = restore_input(resolved_id, selected)
    if selected is None and not multiple:
        selected = _find_first_option(choices_)

    if options is None:
        options = {}

    opts = _update_options(options, remove_button, multiple)

    choices_tags = _render_choices(choices_, selected)

    return div(
        shiny_input_label(resolved_id, label),
        div(
            tags.select(
                *choices_tags,
                {"class": "shiny-input-select"},
                class_=None if selectize else "form-select",
                id=resolved_id,
                multiple=multiple,
                size=size,
            ),
            (
                TagList(
                    tags.script(
                        dumps(opts),
                        type="application/json",
                        data_for=resolved_id,
                        data_eval=dumps(extract_js_keys(opts)),
                    ),
                    selectize_deps(),
                )
                if selectize
                else None
            ),
        ),
        class_="form-group shiny-input-container",
        style=css(width=width),
    )


def _resolve_remove_button(remove_button: Optional[bool], multiple: bool) -> bool:
    if remove_button is None:
        if multiple:
            return True
        else:
            return False
    return remove_button


def _update_options(
    options: dict[str, Any], remove_button: bool, multiple: bool
) -> dict[str, Any]:
    opts = copy.deepcopy(options)
    plugins = opts.get("plugins", [])

    if remove_button:
        if multiple:
            to_add = "remove_button"
        else:
            to_add = "clear_button"

        if to_add not in plugins:
            plugins.append(to_add)

    if not plugins:
        return options

    opts["plugins"] = plugins
    return opts


def _normalize_choices(x: SelectChoicesArg) -> _SelectChoices:
    if x is None:
        raise TypeError("`choices` must be a list, tuple, or dict.")
    elif isinstance(x, (list, tuple)):
        return {k: k for k in x}
    else:
        return x


def _contains_html(x: _SelectChoices) -> bool:
    for v in x.values():
        if isinstance(v, Mapping):
            # Check the `_Choices` values of `_OptGrpChoices`
            for vv in v.values():
                if not isinstance(vv, str):
                    return True
        else:
            if not isinstance(v, str):
                return True
    return False


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
