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
from typing import Any, Iterable, Mapping, Optional, Sequence, Union, cast

from htmltools import Tag, TagAttrs, TagChild, TagList, css, div, tags

from .._docstring import add_example
from ..bookmark import restore_input
from ..module import resolve_id
from ._choices import (
    ChoiceKey,
    ChoiceSelection,
    ChoiceValue,
    normalize_choices_mapping,
    resolve_selected,
)
from ._html_deps_external import selectize_deps
from ._utils import JSEval, extract_js_keys, shiny_input_label

# Canonical format for representing select options. Choice values are strings here:
# `_normalize_choices()` has already coerced them.
_Choices = Mapping[str, str]
_OptGrpChoices = Mapping[str, _Choices]

_SelectChoices = Union[_Choices, _OptGrpChoices]

# Formats available to the user. Choice values are coerced with `str()`, so e.g. the
# `int` keys of a `dict[int, str]` are supported.
SelectChoicesArg = Union[
    # [0, 1, 2] or ("a", "b", "c")
    Sequence[ChoiceValue],
    # {"a": "Choice A", 0: "Choice B"}
    Mapping[ChoiceKey, str],
    # optgroup {"Group A": {"a1": "Choice A1", "a2": "Choice A2"}, "Group B": {}}
    Mapping[ChoiceKey, Mapping[ChoiceKey, str]],
]

# A single choice value, or several.
SelectSelectedArg = Union[
    ChoiceValue,
    Sequence[ChoiceValue],
]


_topics = {"Server value": """
If `multiple=False`, the server value is a string with the value of the selected item.
If `multiple=True`, the server value is a tuple containing the values of the
selected items. When ``multiple=True`` and nothing is selected, this value
will be ``None``.
"""}


@add_example()
def input_selectize(
    id: str,
    label: TagChild,
    choices: SelectChoicesArg,
    *,
    selected: Optional[SelectSelectedArg] = None,
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
        If you want to pass a JavaScript function, wrap the string in
        :func:`~shiny.ui.js_eval`.

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
    selected: Optional[SelectSelectedArg] = None,
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
    selected: Optional[SelectSelectedArg] = None,
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
    else:
        selected = resolve_selected(selected, _choice_value_strings(choices_))

    if options is None:
        options = {}

    opts = _update_options(options, remove_button, multiple)

    choices_tags = _render_choices(choices_, selected)

    select_attrs: TagAttrs = {"class": "shiny-input-select"}

    return div(
        shiny_input_label(resolved_id, label),
        div(
            tags.select(
                *choices_tags,
                select_attrs,
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
    """
    Normalize choices, coercing choice values to `str` so the rendered option
    `value` attributes and the `value` sent in `update_*()` messages agree.
    Optgroup labels and nested choice values get the same treatment.

    See https://github.com/posit-dev/py-shiny/issues/2272.
    """
    if isinstance(x, Iterable) and not isinstance(x, (str, bytes, Mapping)):
        # A sequence's entries are both the choice value and the label, so the label is
        # the value's string form.
        return normalize_choices_mapping({k: str(k) for k in x})
    elif not isinstance(x, Mapping):
        # A bare `str` satisfies `Sequence[ChoiceValue]` statically, but iterating it
        # would turn each character into its own choice.
        raise TypeError("`choices` must be a list, tuple, or dict.")

    # The top-level mapping holds optgroup labels alongside choice values, so a
    # collision there is reported as either one.
    normalized = normalize_choices_mapping(x)

    # The result may mix flat options and optgroups at the top level (e.g.
    # `{"a": "A", "Group B": {...}}`). That matches neither arm of the
    # `_SelectChoices` union, hence the `cast`, but `_render_choices()`
    # checks each value with `isinstance`, so the mix is fine at runtime.
    result: dict[str, Any] = {
        key: (normalize_choices_mapping(value) if isinstance(value, Mapping) else value)
        for key, value in normalized.items()
    }
    return cast(_SelectChoices, result)


def _choice_value_strings(x: _SelectChoices) -> set[str]:
    """
    Collect the choice values of already-normalized choices, for `resolve_selected()`.

    Optgroup labels are not choice values, so only the options nested inside a group are
    collected (never the group key itself). Two groups may hold the same choice value:
    duplicates are legal HTML, and the browser reports only the value, so the options are
    indistinguishable either way.
    """
    values: set[str] = set()
    for key, value in x.items():
        if isinstance(value, Mapping):
            values.update(value.keys())
        else:
            values.add(key)
    return values


def _render_choices(
    x: _SelectChoices, selected: Optional[SelectSelectedArg] = None
) -> TagList:
    return _render_choices_with_selection(x, ChoiceSelection(selected))


def _render_choices_with_selection(
    x: _SelectChoices, selection: ChoiceSelection
) -> TagList:
    result = TagList()

    if x is None:
        return result

    for k, v in x.items():
        if isinstance(v, Mapping):
            result.append(
                tags.optgroup(
                    *(
                        _render_choices_with_selection(
                            cast(_SelectChoices, v), selection
                        )
                    ),
                    label=k,
                )
            )
        else:
            result.append(tags.option(v, value=k, selected=k in selection))

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
