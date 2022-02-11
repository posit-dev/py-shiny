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

import sys
from datetime import date

from typing import Optional, Union, Tuple, List

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal

from htmltools import TagChildArg

from ._input_check_radio import ChoicesArg, _generate_options
from ._input_date import _as_date_attr
from ._input_select import SelectChoicesArg, _normalize_choices, _render_choices
from ._input_slider import SliderValueArg, SliderStepArg, _slider_type, _as_numeric
from .._utils import drop_none
from ..session import Session, require_active_session

# -----------------------------------------------------------------------------
# input_action_button.py
# -----------------------------------------------------------------------------
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
        options = session.process_ui(*option_tags)["html"]

    msg = {
        "label": label,
        "options": options,
        "selected": selected,
    }
    session.send_input_message(id, drop_none(msg))


# -----------------------------------------------------------------------------
# input_slider.py
# -----------------------------------------------------------------------------
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
def update_navs(
    id: str, selected: Optional[str] = None, session: Optional[Session] = None
) -> None:
    session = require_active_session(session)
    msg = {"value": selected}
    session.send_input_message(id, drop_none(msg))
