__all__ = (
    "update_action_button",
    "update_action_link",
    "update_checkbox",
    "update_checkbox_group",
    "update_radio_buttons",
    "update_date",
    "update_date_range",
    "update_numeric",
    "update_select",
    "update_slider",
    "update_text",
    "update_text_area",
    "update_navs",
)

from datetime import date
import sys
from textwrap import dedent
from typing import Optional, Union, Tuple, List

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal

from htmltools import TagChildArg

from .._docstring import doc
from ._input_check_radio import ChoicesArg, _generate_options
from ._input_date import _as_date_attr
from ._input_select import SelectChoicesArg, _normalize_choices, _render_choices
from ._input_slider import SliderValueArg, SliderStepArg, _slider_type, _as_numeric
from .._utils import drop_none
from ..session import Session, require_active_session

_note = dedent(
    """
The input updater functions send a message to the client, telling it to change the
settings of an input object. The messages are collected and sent after all the observers
(including outputs) have finished running.

The syntax of these functions is similar to the functions that created the inputs in the
first place. For example, :func:`~shiny.ui.input_numeric` and
:func:`~update_numeric` take a similar set of arguments.

Any arguments with None values will be ignored; they will not result in any changes to
the input object on the client.

For :func:`~update_radio_buttons`, :func:`~update_checkbox_group`, and
:func:`~update_select`, the set of choices can be cleared by using `choices=[]`.
Similarly, for these inputs, the selected item can be cleared by using `selected=[]`.
"""
)


# -----------------------------------------------------------------------------
# input_action_button.py
# -----------------------------------------------------------------------------
@doc(
    "Change the label and/or icon of an action button on the client.",
    see_also=[":func:`~shiny.input_action_button`"],
    note=_note,
)
def update_action_button(
    id: str,
    *,
    label: Optional[str] = None,
    icon: TagChildArg = None,
    session: Optional[Session] = None,
) -> None:
    session = require_active_session(session)
    # TODO: supporting a TagChildArg for label would require changes to shiny.js
    # https://github.com/rstudio/shiny/issues/1140
    msg = {"label": label, "icon": session.process_ui(icon)["html"] if icon else None}
    session.send_input_message(id, drop_none(msg))


update_action_link = update_action_button

# -----------------------------------------------------------------------------
# input_check_radio.py
# -----------------------------------------------------------------------------
@doc(
    "Change the value of a checkbox input on the client.",
    see_also=[":func:`~shiny.ui.input_checkbox`"],
    note=_note,
)
def update_checkbox(
    id: str,
    *,
    label: Optional[str] = None,
    value: Optional[bool] = None,
    session: Optional[Session] = None,
) -> None:
    session = require_active_session(session)
    msg = {"label": label, "value": value}
    session.send_input_message(id, drop_none(msg))


@doc(
    "Change the value of a checkbox group input on the client.",
    see_also=[":func:`~shiny.ui.input_checkbox_group`"],
    note=_note,
)
def update_checkbox_group(
    id: str,
    *,
    label: Optional[str] = None,
    choices: Optional[ChoicesArg] = None,
    selected: Optional[Union[str, List[str]]] = None,
    inline: bool = False,
    session: Optional[Session] = None,
) -> None:
    _update_choice_input(
        id=id,
        type="checkbox",
        label=label,
        choices=choices,
        selected=selected,
        inline=inline,
        session=session,
    )


@doc(
    "Change the value of a radio input on the client.",
    see_also=[":func:`~shiny.ui.input_radio_buttons`"],
    note=_note,
)
def update_radio_buttons(
    id: str,
    *,
    label: Optional[str] = None,
    choices: Optional[ChoicesArg] = None,
    selected: Optional[str] = None,
    inline: bool = False,
    session: Optional[Session] = None,
) -> None:
    _update_choice_input(
        id=id,
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
    selected: Optional[Union[str, List[str]]] = None,
    inline: bool = False,
    session: Optional[Session] = None,
) -> None:
    session = require_active_session(session)
    options = None
    if choices is not None:
        opts = _generate_options(
            id=id, type=type, choices=choices, selected=selected, inline=inline
        )
        options = session.process_ui(opts)["html"]
    msg = {"label": label, "options": options, "value": selected}
    session.send_input_message(id, drop_none(msg))


# -----------------------------------------------------------------------------
# input_date.py
# -----------------------------------------------------------------------------
@doc(
    "Change the value of a date input on the client.",
    parameters={
        "value": """
        The starting date. Either a `date()` object, or a string in yyyy-mm-dd format.
        If `None` (the default), will use the current date in the client's time zone.
        """
    },
    see_also=[":func:`~shiny.ui.input_date"],
    note=_note,
)
def update_date(
    id: str,
    *,
    label: Optional[str] = None,
    value: Optional[Union[date, str]] = None,
    min: Optional[Union[date, str]] = None,
    max: Optional[Union[date, str]] = None,
    session: Optional[Session] = None,
) -> None:

    session = require_active_session(session)
    msg = {
        "label": label,
        "value": _as_date_attr(value),
        "min": _as_date_attr(min),
        "max": _as_date_attr(max),
    }
    session.send_input_message(id, drop_none(msg))


@doc(
    "Change the start and end values of a date range input on the client.",
    see_also=[":func:`~shiny.ui.input_date_range"],
    note=_note,
)
def update_date_range(
    id: str,
    *,
    label: Optional[str] = None,
    start: Optional[Union[date, str]] = None,
    end: Optional[Union[date, str]] = None,
    min: Optional[Union[date, str]] = None,
    max: Optional[Union[date, str]] = None,
    session: Optional[Session] = None,
) -> None:
    session = require_active_session(session)
    value = {"start": _as_date_attr(start), "end": _as_date_attr(end)}
    msg = {
        "label": label,
        "value": drop_none(value),
        "min": _as_date_attr(min),
        "max": _as_date_attr(max),
    }
    session.send_input_message(id, drop_none(msg))


# -----------------------------------------------------------------------------
# input_numeric.py
# -----------------------------------------------------------------------------
@doc(
    "Change the value of a number input on the client.",
    see_also=[":func:`~shiny.ui.input_numeric`"],
    note=_note,
)
def update_numeric(
    id: str,
    *,
    label: Optional[str] = None,
    value: Optional[float] = None,
    min: Optional[float] = None,
    max: Optional[float] = None,
    step: Optional[float] = None,
    session: Optional[Session] = None,
) -> None:
    session = require_active_session(session)
    msg = {
        "label": label,
        "value": value,
        "min": min,
        "max": max,
        "step": step,
    }
    session.send_input_message(id, drop_none(msg))


# -----------------------------------------------------------------------------
# input_select.py
# -----------------------------------------------------------------------------
@doc(
    "Change the value of a select input on the client.",
    see_also=[":func:`~shiny.ui.input_select`"],
    note=_note,
)
def update_select(
    id: str,
    *,
    label: Optional[str] = None,
    choices: Optional[SelectChoicesArg] = None,
    selected: Optional[str] = None,
    session: Optional[Session] = None,
) -> None:
    session = require_active_session(session)

    if choices is None:
        options = None
    else:
        option_tags = _render_choices(_normalize_choices(choices), selected)
        # Typing problem due to a bug in pylance:
        # https://github.com/microsoft/pylance-release/issues/2377
        options = session.process_ui(option_tags)["html"]  # type: ignore

    msg = {
        "label": label,
        "options": options,
        "selected": selected,
    }
    session.send_input_message(id, drop_none(msg))


# -----------------------------------------------------------------------------
# input_slider.py
# -----------------------------------------------------------------------------
@doc(
    "Change the value of a slider input on the client.",
    parameters={
        "step": """
    Specifies the interval between each selectable value on the slider. Either `None`
    (the default), which uses a heuristic to determine the step size or a single
    number. If the values are dates, step is in days; if the values are date-times,
    step is in seconds.
    """
    },
    see_also=[":func:`~shiny.ui.input_slider"],
    note=_note,
)
def update_slider(
    id: str,
    *,
    label: Optional[str] = None,
    value: Optional[
        Union[SliderValueArg, Tuple[SliderValueArg, SliderValueArg]]
    ] = None,
    min: Optional[SliderValueArg] = None,
    max: Optional[SliderValueArg] = None,
    step: Optional[SliderStepArg] = None,
    time_format: Optional[str] = None,
    timezone: Optional[str] = None,
    session: Optional[Session] = None,
) -> None:
    session = require_active_session(session)

    # Get any non-None value to see if the `data-type` may need to change
    val = value[0] if isinstance(value, tuple) else value
    present_val = next((x for x in [val, min, max]), None)

    data_type = None if present_val is None else _slider_type(present_val)
    if time_format is None and data_type and data_type[0:4] == "date":
        time_format = "%F" if data_type == "date" else "%F %T"

    min_num = None if min is None else _as_numeric(min)
    max_num = None if max is None else _as_numeric(max)
    step_num = None if step is None else _as_numeric(step)

    msg = {
        "label": label,
        "value": value,
        "min": min_num,
        "max": max_num,
        "step": step_num,
        "data-type": data_type,
        "time_format": time_format,
        "timezone": timezone,
    }
    session.send_input_message(id, drop_none(msg))


# -----------------------------------------------------------------------------
# input_text.py
# -----------------------------------------------------------------------------
@doc(
    "Change the value of a text input on the client.",
    see_also=[":func:`~shiny.ui.input_text`"],
    note=_note,
)
def update_text(
    id: str,
    *,
    label: Optional[str] = None,
    value: Optional[str] = None,
    placeholder: Optional[str] = None,
    session: Optional[Session] = None,
) -> None:
    session = require_active_session(session)
    msg = {"label": label, "value": value, "placeholder": placeholder}
    session.send_input_message(id, drop_none(msg))


update_text_area = update_text


# -----------------------------------------------------------------------------
# navs.py
# -----------------------------------------------------------------------------

# TODO: we should probably provide a nav_select() alias for this as well
@doc(
    "Change the value of a navs container on the client.",
    see_also=[
        ":func:`shiny.ui.navs_tab",
        ":func:`shiny.ui.navs_pill",
        ":func:`shiny.ui.page_navbar",
    ],
    note=_note,
)
def update_navs(
    id: str, selected: Optional[str] = None, session: Optional[Session] = None
) -> None:
    session = require_active_session(session)
    msg = {"value": selected}
    session.send_input_message(id, drop_none(msg))
