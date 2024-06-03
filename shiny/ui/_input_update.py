from __future__ import annotations

__all__ = (
    "update_action_button",
    "update_action_link",
    "update_checkbox",
    "update_switch",
    "update_checkbox_group",
    "update_radio_buttons",
    "update_date",
    "update_date_range",
    "update_numeric",
    "update_select",
    "update_selectize",
    "update_slider",
    "update_text",
    "update_text_area",
    "update_navs",
)

import json
import re
from datetime import date
from typing import TYPE_CHECKING, Literal, Mapping, Optional, cast, overload

from htmltools import TagChild, TagList, tags
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from .._deprecated import _session_param_docs as _session_param
from .._docstring import add_example, doc_format, no_example
from .._namespaces import ResolvedId, resolve_id
from .._typing_extensions import NotRequired, TypedDict
from .._utils import drop_none
from ..input_handler import input_handlers
from ..session import require_active_session, session_context
from ..types import MISSING, MISSING_TYPE, ActionButtonValue
from ._input_check_radio import ChoicesArg, _generate_options
from ._input_date import _as_date_attr
from ._input_select import SelectChoicesArg, _normalize_choices, _render_choices
from ._input_slider import SliderStepArg, SliderValueArg, _as_numeric, _slider_type
from ._utils import JSEval, extract_js_keys, session_on_flush_send_msg

if TYPE_CHECKING:
    from ..session import Session


_note = """
    The input updater functions send a message to the client, telling it to change the
    settings of an input object. The messages are collected and sent after all the
    observers (including outputs) have finished running.

    The syntax of these functions is similar to the functions that created the inputs in
    the first place. For example, :func:`~shiny.ui.input_numeric` and
    :func:`~shiny.ui.update_numeric` take a similar set of arguments.

    Any arguments with ``None`` values will be ignored; they will not result in any
    changes to the input object on the client.

    For :func:`~shiny.ui.update_radio_buttons`, :func:`~shiny.ui.update_checkbox_group`, and
    :func:`~shiny.ui.update_select`, the set of choices can be cleared by using ``choices=[]``.
    Similarly, for these inputs, the selected item can be cleared by using
    `selected=[]`.
"""


# -----------------------------------------------------------------------------
# input_action_button.py
# -----------------------------------------------------------------------------
@add_example()
@doc_format(note=_note, session_param=_session_param)
def update_action_button(
    id: str,
    *,
    label: Optional[str] = None,
    icon: TagChild = None,
    session: MISSING_TYPE = MISSING,
) -> None:
    """
    Change the label and/or icon of an action button on the client.

    Parameters
    ----------
    id
        An input id.
    label
        An input label.
    icon
        An icon to appear inline with the button/link.
    {session_param}

    Note
    ----
    {note}

    See Also
    --------
    * :func:`~shiny.input_action_button`
    """

    active_session = require_active_session(session)
    # TODO: supporting a TagChild for label would require changes to shiny.js
    # https://github.com/rstudio/shiny/issues/1140
    msg = {
        "label": label,
        "icon": active_session._process_ui(icon)["html"] if icon else None,
    }
    active_session.send_input_message(id, drop_none(msg))


update_action_link = update_action_button
update_action_link.__doc__ = update_action_button.__doc__


# -----------------------------------------------------------------------------
# input_task_button.py
# -----------------------------------------------------------------------------
@no_example()
def update_task_button(
    id: str,
    *,
    state: Optional[str] = None,
    session: MISSING_TYPE = MISSING,
) -> None:
    """
    Change the state of a task button on the client.

    When a task button is clicked, it automatically changes to the "busy" state. This
    function can be used to change the state back to "ready" when the task is complete.

    You can also use this function to change the state to "busy" manually, which will
    prevent the button from automatically resetting to "ready" after a click.

    Parameters
    ----------
    id
        An input id.
    state
        The new state of the button. One of "ready", "busy", or a custom state name
        added via :func:`~shiny.ui.input_task_button`.
    session
        A :class:`~shiny.Session` instance. If not provided, it is inferred via
        :func:`~shiny.session.get_current_session`.
    """

    active_session = require_active_session(session)

    if state is not None:
        resolved_id = active_session.ns(id)
        if state != "ready":
            manual_task_reset_buttons.add(resolved_id)
        else:
            manual_task_reset_buttons.discard(resolved_id)

    msg = {"state": state}
    active_session.send_input_message(id, drop_none(msg))


manual_task_reset_buttons: set[ResolvedId] = set()


@input_handlers.add("bslib.taskbutton")
def _(
    value: dict[str, object], name: ResolvedId, session: Session
) -> ActionButtonValue:
    if value["autoReset"]:

        @session.on_flush
        def callback() -> None:
            # This is input_task_button's auto-reset feature: unless the button has
            # opted out using set_task_button_manual_reset(), we should reset after a
            # flush cycle where a bslib.taskbutton value is seen.
            if ResolvedId(name) not in manual_task_reset_buttons:
                with session_context(session):
                    update_task_button(name, state="ready")

    return ActionButtonValue(cast(int, value["value"]))


# -----------------------------------------------------------------------------
# input_check_radio.py
# -----------------------------------------------------------------------------
@add_example()
@doc_format(note=_note, session_param=_session_param)
def update_checkbox(
    id: str,
    *,
    label: Optional[str] = None,
    value: Optional[bool] = None,
    session: MISSING_TYPE = MISSING,
) -> None:
    """
    Change the value of a checkbox input on the client.

    Parameters
    ----------
    id
        An input id.
    label
        An input label.
    value
        A new value.
    {session_param}

    Note
    ----
    {note}

    See Also
    --------
    * :func:`~shiny.ui.input_checkbox`
    """

    active_session = require_active_session(session)
    msg = {"label": label, "value": value}
    active_session.send_input_message(id, drop_none(msg))


@no_example()
@doc_format(note=_note, session_param=_session_param)
def update_switch(
    id: str,
    *,
    label: Optional[str] = None,
    value: Optional[bool] = None,
    session: MISSING_TYPE = MISSING,
) -> None:
    """
    Change the value of a switch input on the client.

    Parameters
    ----------
    id
        An input id.
    label
        An input label.
    value
        A new value.
    {session_param}

    Note
    ----
    {note}

    See Also
    --------
    * :func:`~shiny.ui.input_switch`
    """

    active_session = require_active_session(session)
    msg = {"label": label, "value": value}
    active_session.send_input_message(id, drop_none(msg))


@add_example()
@doc_format(note=_note, session_param=_session_param)
def update_checkbox_group(
    id: str,
    *,
    label: Optional[str] = None,
    choices: Optional[ChoicesArg] = None,
    selected: Optional[str | list[str] | tuple[str, ...]] = None,
    inline: bool = False,
    session: MISSING_TYPE = MISSING,
) -> None:
    """
    Change the value of a checkbox group input on the client.

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
    {session_param}

    Note
    ----
    {note}

    See Also
    --------
    * :func:`~shiny.ui.input_checkbox_group`
    """

    _update_choice_input(
        id=resolve_id(id),
        type="checkbox",
        label=label,
        choices=choices,
        selected=selected,
        inline=inline,
        session=session,
    )


@add_example()
@doc_format(note=_note, session_param=_session_param)
def update_radio_buttons(
    id: str,
    *,
    label: Optional[str] = None,
    choices: Optional[ChoicesArg] = None,
    selected: Optional[str] = None,
    inline: bool = False,
    session: MISSING_TYPE = MISSING,
) -> None:
    """
    Change the value of a radio input on the client.

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
        If ``True```, the result is displayed inline
    {session_param}

    Note
    ----
    {note}

    See Also
    --------
    * :func:`~shiny.ui.input_radio_buttons`
    """

    _update_choice_input(
        id=resolve_id(id),
        type="radio",
        label=label,
        choices=choices,
        selected=selected,
        inline=inline,
        session=session,
    )


def _update_choice_input(
    id: str,
    *,
    type: Literal["checkbox", "radio"],
    label: Optional[str] = None,
    choices: Optional[ChoicesArg] = None,
    selected: Optional[str | list[str] | tuple[str, ...]] = None,
    inline: bool = False,
    session: MISSING_TYPE = MISSING,
) -> None:
    active_session = require_active_session(session)
    options = None
    if choices is not None:
        # https://github.com/posit-dev/py-shiny/issues/708#issuecomment-1696352934
        with session_context(active_session):
            resolved_id = resolve_id(id)

        opts = _generate_options(
            id=resolved_id,
            type=type,
            choices=choices,
            selected=selected,
            inline=inline,
        )
        options = active_session._process_ui(opts)["html"]
    msg = {"label": label, "options": options, "value": selected}
    active_session.send_input_message(id, drop_none(msg))


# -----------------------------------------------------------------------------
# input_date.py
# -----------------------------------------------------------------------------
@add_example()
@doc_format(note=_note, session_param=_session_param)
def update_date(
    id: str,
    *,
    label: Optional[str] = None,
    value: Optional[date | str] = None,
    min: Optional[date | str] = None,
    max: Optional[date | str] = None,
    session: MISSING_TYPE = MISSING,
) -> None:
    """
    Change the value of a date input on the client.

    Parameters
    ----------
    id
        An input id.
    label
        An input label.
    value
        The starting date. Either a `date()` object, or a string in yyyy-mm-dd format.
        If ``None`` (the default), will use the current date in the client's time zone.
    min
        The minimum allowed value.
    max
        The maximum allowed value.
    {session_param}

    Note
    ----
    {note}

    See Also
    --------
    * :func:`~shiny.ui.input_date`
    """

    active_session = require_active_session(session)
    msg = {
        "label": label,
        "value": _as_date_attr(value),
        "min": _as_date_attr(min),
        "max": _as_date_attr(max),
    }
    active_session.send_input_message(id, drop_none(msg))


@add_example()
@doc_format(note=_note, session_param=_session_param)
def update_date_range(
    id: str,
    *,
    label: Optional[str] = None,
    start: Optional[date | str] = None,
    end: Optional[date | str] = None,
    min: Optional[date | str] = None,
    max: Optional[date | str] = None,
    session: MISSING_TYPE = MISSING,
) -> None:
    """
    Change the start and end values of a date range input on the client.

    Parameters
    ----------
    id
        An input id.
    label
        An input label.
    start
        The initial start date. Either a :class:`~datetime.date` object, or a string in
        yyyy-mm-dd format. If ``None`` (the default), will use the current date in the
        client's time zone.
    end
        The initial end date. Either a :class:`~datetime.date` object, or a string in
        yyyy-mm-dd format. If ``None`` (the default), will use the current date in the
        client's time zone.
    min
        The minimum allowed value.
    max
        The maximum allowed value.
    {session_param}

    Note
    ----
    {note}

    See Also
    --------
    * :func:`~shiny.ui.input_date_range`
    """

    active_session = require_active_session(session)
    value = {"start": _as_date_attr(start), "end": _as_date_attr(end)}
    msg = {
        "label": label,
        "value": drop_none(value),
        "min": _as_date_attr(min),
        "max": _as_date_attr(max),
    }
    active_session.send_input_message(id, drop_none(msg))


# -----------------------------------------------------------------------------
# input_numeric.py
# -----------------------------------------------------------------------------
@add_example()
@doc_format(note=_note, session_param=_session_param)
def update_numeric(
    id: str,
    *,
    label: Optional[str] = None,
    value: Optional[float] = None,
    min: Optional[float] = None,
    max: Optional[float] = None,
    step: Optional[float] = None,
    session: MISSING_TYPE = MISSING,
) -> None:
    """
    Change the value of a number input on the client.

    Parameters
    ----------
    id
        An input id.
    label
        An input label.
    value
        A new value.
    min
        The minimum allowed value.
    max
        The maximum allowed value.
    step
        Interval to use when stepping between min and max.
    {session_param}

    Note
    ----
    {note}

    See Also
    --------
    * :func:`~shiny.ui.input_numeric`
    """

    active_session = require_active_session(session)
    msg = {
        "label": label,
        "value": value,
        "min": min,
        "max": max,
        "step": step,
    }
    active_session.send_input_message(id, drop_none(msg))


# -----------------------------------------------------------------------------
# input_select.py
# -----------------------------------------------------------------------------
@add_example()
@doc_format(note=_note, session_param=_session_param)
def update_select(
    id: str,
    *,
    label: Optional[str] = None,
    choices: Optional[SelectChoicesArg] = None,
    selected: Optional[str | list[str]] = None,
    session: MISSING_TYPE = MISSING,
) -> None:
    """
    Change the value of a select input on the client.

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
    {session_param}

    Note
    ----
    {note}

    See Also
    --------
    * :func:`~shiny.ui.input_select`
    * :func:`~shiny.ui.update_selectize`
    """

    active_session = require_active_session(session)

    selected_values = selected
    if isinstance(selected, str):
        selected_values = [selected]

    if choices is None:
        options = None
    else:
        option_tags = _render_choices(_normalize_choices(choices), selected)
        options = active_session._process_ui(option_tags)["html"]

    msg = {
        "label": label,
        "options": options,
        "value": selected_values,
    }
    active_session.send_input_message(id, drop_none(msg))


class FlatSelectChoice(TypedDict):
    label: str
    value: str
    optgroup: NotRequired[str]


@add_example()
@doc_format(note=_note, session_param=_session_param)
def update_selectize(
    id: str,
    *,
    label: Optional[str] = None,
    choices: Optional[SelectChoicesArg] = None,
    selected: Optional[str | list[str]] = None,
    options: Optional[dict[str, str | float | JSEval]] = None,
    server: bool = False,
    session: MISSING_TYPE = MISSING,
) -> None:
    """
    Change the value of a selectize.js powered input on the client.

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
    options
        Options to send to update, see `input_selectize` for details.
    server
        Whether to store choices on the server side, and load the select options
        dynamically on searching, instead of writing all choices into the page at once
        (i.e., only use the client-side version of selectize.js)
    {session_param}

    Note
    ----
    {note}

    See Also
    --------
    * :func:`~shiny.ui.input_selectize`
    """

    active_session = require_active_session(session)

    if not server:
        with session_context(active_session):
            return update_select(
                id,
                label=label,
                choices=choices,
                selected=selected,
            )

    if options is not None:
        cfg = TagList(
            tags.script(
                json.dumps(options),
                type="application/json",
                data_for=id,
                data_eval=json.dumps(extract_js_keys(options)),
            )
        )
        active_session.send_input_message(
            id,
            drop_none({"config": cfg.get_html_string()}),
        )

    # Transform choices to a list of dicts (this is the form the client wants)
    # [{"label": "Foo", "value": "foo", "optgroup": "foo"}, ...]
    flat_choices: list[FlatSelectChoice] = []
    if choices is not None:
        for k, v in _normalize_choices(choices).items():
            if not isinstance(v, Mapping):
                flat_choices.append(
                    FlatSelectChoice(
                        value=k, label=active_session._process_ui(v)["html"]
                    )
                )
            else:  # The optgroup case
                flat_choices.extend(
                    [
                        FlatSelectChoice(
                            optgroup=k,
                            value=k2,
                            label=active_session._process_ui(v2)["html"],
                        )
                        for (k2, v2) in v.items()
                    ]
                )

    selected_values = selected
    if isinstance(selected, str):
        selected_values = [selected]

    # Find any selected choices now so we have them ready to send to the client
    if selected_values is None:
        selected_choices = []
    else:
        selected_choices = [x for x in flat_choices if x["value"] in selected_values]

    def selectize_choices_json(request: Request) -> Response:
        if choices is None:
            return Response([], status_code=200)

        # N.B. relevant query parameters that shiny.js setscan be found here
        # https://github.com/rstudio/shiny/blob/78d77ce/srcts/src/bindings/input/selectInput.ts#L138-L142
        qparams = request.query_params

        # The (space-separated) input value(s) in lower-case (for case-insensitive matching)
        keywords = set(re.split(r"\s+", qparams.get("query", "").lower()))

        # Also note that the user (at least someday) has the ability to customize any of
        # these options https://github.com/rstudio/shiny/blob/78d77ce/srcts/src/bindings/input/selectInput.ts#L231
        #
        # For most options this is fine, but searchField/valueField require some validation.

        # i.e. maxOptions (defaults to 1000)
        max_options = int(qparams.get("maxop", 1000))

        # i.e. searchConjunction (defaults to 'and', but can also be 'or')
        conjunction = any if qparams.get("conju", "and") == "or" else all

        # i.e. searchFields (defaults to ['label'])
        search_fields: list[str] = json.loads(qparams.get("field", "['label']"))
        if len(search_fields) == 0:
            raise ValueError("The selectize.js searchFields option must be non-empty")

        # For some odd (probably wrong) reason, shiny.js is wrapping searchFields in an additional array
        # https://github.com/rstudio/shiny/blob/78d77ce/srcts/src/bindings/input/selectInput.ts#L139
        # https://github.com/rstudio/shiny/blob/78d77c/R/update-input.R#L801
        if isinstance(search_fields[0], list):
            search_fields = search_fields[0]

        if set(search_fields).difference(set(["label", "value", "optgroup"])):
            raise ValueError(
                "The selectize.js searchFields option must contain some combination of: "
                + "'label', 'value', and 'optgroup'"
            )

        # i.e. valueField (defaults to 'value')
        if qparams.get("value", "value") != "value":
            raise ValueError(
                "The selectize.js valueField option must be set to 'value'"
            )

        filtered_choices: list[FlatSelectChoice] = []
        for choice in flat_choices:
            # Short-circuit if we've reached the max number of options
            if (len(filtered_choices) + len(selected_choices)) > max_options:
                break

            # If this is a selected value, *don't* add it here (add after this loop)
            if selected_values and choice["value"] in selected_values:
                continue

            match = False
            for f in search_fields:
                val: Optional[str] = choice.get(f, None)
                # optgroup could be requested, but not necessarily present/relevant
                if val is None:
                    continue
                if conjunction([x in val.lower() for x in keywords]):
                    match = True

            if match:
                filtered_choices.append(choice)

        if selected_choices:
            filtered_choices.extend(selected_choices)

        return JSONResponse(filtered_choices, status_code=200)

    msg = {
        "label": label,
        "value": selected_values,
        "url": active_session.dynamic_route(
            f"update_selectize_{id}", selectize_choices_json
        ),
    }

    return active_session.send_input_message(id, drop_none(msg))


# -----------------------------------------------------------------------------
# input_slider.py
# -----------------------------------------------------------------------------
@add_example()
@doc_format(note=_note, session_param=_session_param)
def update_slider(
    id: str,
    *,
    label: Optional[str] = None,
    value: Optional[SliderValueArg | tuple[SliderValueArg, SliderValueArg]] = None,
    min: Optional[SliderValueArg] = None,
    max: Optional[SliderValueArg] = None,
    step: Optional[SliderStepArg] = None,
    time_format: Optional[str] = None,
    timezone: Optional[str] = None,
    session: MISSING_TYPE = MISSING,
) -> None:
    """
    Change the value of a slider input on the client.

    Parameters
    ----------
    id
        An input id.
    label
        An input label.
    value
        A new value.
    min
        The minimum allowed value.
    max
        The maximum allowed value.
    step
        Specifies the interval between each selectable value on the slider. Either
        ``None`` (the default), which uses a heuristic to determine the step size or a
        single number. If the values are dates, step is in days; if the values are
        date-times, step is in seconds.
    time_format
        Only used if the slider values are :class:`~datetime.date` or
        :class:`~datetime.datetime` objects. A time format string, to be passed to the
        Javascript strftime library. See https://github.com/samsonjs/strftime for more
        details. For Dates, the default is "%F" (like "2015-07-01"), and for Datetimes,
        the default is "%F %T" (like "2015-07-01 15:32:10").
    timezone
        Only used if the values are :class:`~datetime.datetime` objects. A string
        specifying the time zone offset for the displayed times, in the format "+HHMM"
        or "-HHMM". If ``None`` (the default), times will be displayed in the browser's
        time zone. The value "+0000" will result in UTC time.
    {session_param}

    Note
    ----
    {note}

    See Also
    --------
    * :func:`~shiny.ui.input_slider`
    """

    active_session = require_active_session(session)

    # Get any non-None value to see if the `data-type` may need to change
    val = value[0] if isinstance(value, (tuple, list)) else value
    present_val = next((x for x in [val, min, max] if x is not None), None)

    data_type = None if present_val is None else _slider_type(present_val)
    if time_format is None and data_type and data_type[0:4] == "date":
        time_format = "%F" if data_type == "date" else "%F %T"

    min_num = None if min is None else _as_numeric(min)
    max_num = None if max is None else _as_numeric(max)
    step_num = None if step is None else _as_numeric(step)
    if isinstance(value, (tuple, list)):
        value_num = [_as_numeric(x) for x in value]
    elif value is not None:
        value_num = _as_numeric(value)
    else:
        value_num = None

    msg = {
        "label": label,
        "value": value_num,
        "min": min_num,
        "max": max_num,
        "step": step_num,
        "data-type": data_type,
        "time_format": time_format,
        "timezone": timezone,
    }
    active_session.send_input_message(id, drop_none(msg))


# -----------------------------------------------------------------------------
# input_text.py
# -----------------------------------------------------------------------------
@add_example()
@doc_format(note=_note, session_param=_session_param)
def update_text(
    id: str,
    *,
    label: Optional[str] = None,
    value: Optional[str] = None,
    placeholder: Optional[str] = None,
    session: MISSING_TYPE = MISSING,
) -> None:
    """
    Change the value of a text input on the client.

    Parameters
    ----------
    id
        An input id.
    label
        An input label.
    value
        A new value.
    placeholder
        A hint as to what can be entered into the control.
    {session_param}

    Note
    ----
    {note}

    See Also
    --------
    * :func:`~shiny.ui.input_text`
    """

    active_session = require_active_session(session)
    msg = {"label": label, "value": value, "placeholder": placeholder}
    active_session.send_input_message(id, drop_none(msg))


update_text_area = update_text
update_text_area.__doc__ = update_text.__doc__


# -----------------------------------------------------------------------------
# navs.py
# -----------------------------------------------------------------------------


# TODO: we should probably provide a nav_select() alias for this as well
@add_example()
@doc_format(note=_note, session_param=_session_param)
def update_navs(
    id: str,
    selected: Optional[str] = None,
    session: MISSING_TYPE = MISSING,
) -> None:
    """
    Change the value of a navs container on the client.

    Parameters
    ----------
    id
        An input id.
    selected
        The values that should be initially selected, if any.
    {session_param}

    Note
    ----
    {note}

    See Also
    --------
    * :func:`~shiny.ui.navset_tab`
    * :func:`~shiny.ui.navset_pill`
    * :func:`~shiny.ui.page_navbar`
    """

    active_session = require_active_session(session)
    msg = {"value": selected}
    active_session.send_input_message(id, drop_none(msg))


# -----------------------------------------------------------------------------
# tooltips.py
# -----------------------------------------------------------------------------
@add_example()
def update_tooltip(
    id: str,
    *args: TagChild,
    show: Optional[bool] = None,
) -> None:
    """
    Update tooltip contents.

    Parameters
    ----------
    id
        A character string that matches an existing tooltip id.
    *args
        Contents to the tooltip's body.
    show
        Opens (`True`) or closes (`False`) the tooltip.
    """

    session_on_flush_send_msg(
        id,
        drop_none(
            {
                "method": "update",
                "title": (
                    require_active_session()._process_ui(TagList(*args))
                    if len(args) > 0
                    else None
                ),
            }
        ),
    )
    if show is not None:
        session_on_flush_send_msg(
            id,
            {
                "method": "toggle",
                "value": _normalize_show_value(show),
            },
        )


# -----------------------------------------------------------------------------
# popover.py
# -----------------------------------------------------------------------------


@add_example()
@doc_format(session_param=_session_param)
def update_popover(
    id: str,
    *args: TagChild,
    title: Optional[TagChild] = None,
    show: Optional[bool] = None,
) -> None:
    """
    Update the contents or title of a popover.

    Parameters
    ----------
    id
        The id of the popover DOM element to update.
    *args
        The new contents of the popover.
    title
        The new title of the popover.
    show
        Opens (`True`) or closes (`False`) the popover.

    See Also
    --------
    * :func:`~shiny.ui.popover`
    """

    if title is not None or len(args) > 0:
        session = require_active_session()
        session_on_flush_send_msg(
            id,
            drop_none(
                {
                    "method": "update",
                    "content": (
                        session._process_ui(TagList(*args)) if len(args) > 0 else None
                    ),
                    "header": session._process_ui(title) if title is not None else None,
                },
            ),
        )
    if show is not None:
        session_on_flush_send_msg(
            id,
            {
                "method": "toggle",
                "value": _normalize_show_value(show),
            },
        )


@overload
def _normalize_show_value(show: None) -> Literal["toggle"]: ...


@overload
def _normalize_show_value(show: bool) -> Literal["show", "hide"]: ...


def _normalize_show_value(show: bool | None) -> Literal["toggle", "show", "hide"]:
    if show is None:
        return "toggle"
    return "show" if show else "hide"
