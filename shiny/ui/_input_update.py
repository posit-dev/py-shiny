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
from typing import Optional, Union, Tuple, List

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal

from htmltools import TagChildArg

from .._docstring import doc_format, add_example
from ._input_check_radio import ChoicesArg, _generate_options
from ._input_date import _as_date_attr
from ._input_select import SelectChoicesArg, _normalize_choices, _render_choices
from ._input_slider import SliderValueArg, SliderStepArg, _slider_type, _as_numeric
from .._utils import drop_none
from ..session import Session, require_active_session

_note = """
    The input updater functions send a message to the client, telling it to change the
    settings of an input object. The messages are collected and sent after all the
    observers (including outputs) have finished running.

    The syntax of these functions is similar to the functions that created the inputs in
    the first place. For example, :func:`~shiny.ui.input_numeric` and
    :func:`~update_numeric` take a similar set of arguments.

    Any arguments with ``None`` values will be ignored; they will not result in any
    changes to the input object on the client.

    For :func:`~update_radio_buttons`, :func:`~update_checkbox_group`, and
    :func:`~update_select`, the set of choices can be cleared by using ``choices=[]``.
    Similarly, for these inputs, the selected item can be cleared by using
    `selected=[]`.
"""


# -----------------------------------------------------------------------------
# input_action_button.py
# -----------------------------------------------------------------------------
@doc_format(note=_note)
@add_example()
def update_action_button(
    id: str,
    *,
    label: Optional[str] = None,
    icon: TagChildArg = None,
    session: Optional[Session] = None,
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
    session
        A :class:`~shiny.Session` instance. If not provided, it is inferred via
       :func:`~shiny.session.get_current_session`.

    Note
    ----
    {note}

    See Also
    -------
    :func:`~shiny.input_action_button`
    """

    session = require_active_session(session)
    # TODO: supporting a TagChildArg for label would require changes to shiny.js
    # https://github.com/rstudio/shiny/issues/1140
    msg = {"label": label, "icon": session._process_ui(icon)["html"] if icon else None}
    session.send_input_message(id, drop_none(msg))


update_action_link = update_action_button
update_action_link.__doc__ = update_action_button.__doc__

# -----------------------------------------------------------------------------
# input_check_radio.py
# -----------------------------------------------------------------------------
@doc_format(note=_note)
@add_example()
def update_checkbox(
    id: str,
    *,
    label: Optional[str] = None,
    value: Optional[bool] = None,
    session: Optional[Session] = None,
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
    session
        A :class:`~shiny.Session` instance. If not provided, it is inferred via
       :func:`~shiny.session.get_current_session`.

    Note
    ----
    {note}

    See Also
    -------
    ~shiny.ui.input_checkbox
    """

    session = require_active_session(session)
    msg = {"label": label, "value": value}
    session.send_input_message(id, drop_none(msg))


@doc_format(note=_note)
@add_example()
def update_checkbox_group(
    id: str,
    *,
    label: Optional[str] = None,
    choices: Optional[ChoicesArg] = None,
    selected: Optional[Union[str, List[str]]] = None,
    inline: bool = False,
    session: Optional[Session] = None,
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
    session
        A :class:`~shiny.Session` instance. If not provided, it is inferred via
       :func:`~shiny.session.get_current_session`.

    Note
    ----
    {note}

    See Also
    -------
    ~shiny.ui.input_checkbox_group
    """

    _update_choice_input(
        id=id,
        type="checkbox",
        label=label,
        choices=choices,
        selected=selected,
        inline=inline,
        session=session,
    )


@doc_format(note=_note)
@add_example()
def update_radio_buttons(
    id: str,
    *,
    label: Optional[str] = None,
    choices: Optional[ChoicesArg] = None,
    selected: Optional[str] = None,
    inline: bool = False,
    session: Optional[Session] = None,
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
    session
        A :class:`~shiny.Session` instance. If not provided, it is inferred via
       :func:`~shiny.session.get_current_session`.

    Note
    ----
    {note}

    See Also
    -------
    ~shiny.ui.input_radio_buttons
    """

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
        options = session._process_ui(opts)["html"]
    msg = {"label": label, "options": options, "value": selected}
    session.send_input_message(id, drop_none(msg))


# -----------------------------------------------------------------------------
# input_date.py
# -----------------------------------------------------------------------------
@doc_format(note=_note)
@add_example()
def update_date(
    id: str,
    *,
    label: Optional[str] = None,
    value: Optional[Union[date, str]] = None,
    min: Optional[Union[date, str]] = None,
    max: Optional[Union[date, str]] = None,
    session: Optional[Session] = None,
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
    session
        A :class:`~shiny.Session` instance. If not provided, it is inferred via
       :func:`~shiny.session.get_current_session`.

    Note
    ----
    {note}

    See Also
    -------
    ~shiny.ui.input_date
    """

    session = require_active_session(session)
    msg = {
        "label": label,
        "value": _as_date_attr(value),
        "min": _as_date_attr(min),
        "max": _as_date_attr(max),
    }
    session.send_input_message(id, drop_none(msg))


@doc_format(note=_note)
@add_example()
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
    """
    Change the start and end values of a date range input on the client.

    Parameters
    ----------
    id
        An input id.
    label
        An input label.
    start
        The initial start date. Either a :func:`~datetime.date` object, or a string in
        yyyy-mm-dd format. If ``None`` (the default), will use the current date in the
        client's time zone.
    end
        The initial end date. Either a :func:`~datetime.date` object, or a string in
        yyyy-mm-dd format. If ``None`` (the default), will use the current date in the
        client's time zone.
    min
        The minimum allowed value.
    max
        The maximum allowed value.
    session
        A :class:`~shiny.Session` instance. If not provided, it is inferred via
       :func:`~shiny.session.get_current_session`.

    Note
    ----
    {note}

    See Also
    -------
    ~shiny.ui.input_date_range
    """

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
@doc_format(note=_note)
@add_example()
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
    session
        The :class:`~shiny.Session` object passed to the server function of a :func:`~shiny.App`.

    Note
    ----
    {note}

    See Also
    -------
    ~shiny.ui.input_numeric
    """

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
@doc_format(note=_note)
@add_example()
def update_select(
    id: str,
    *,
    label: Optional[str] = None,
    choices: Optional[SelectChoicesArg] = None,
    selected: Optional[str] = None,
    session: Optional[Session] = None,
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
        ``<optgroup>``
    labels. selected
        The values that should be initially selected, if any.
    session
        A :class:`~shiny.Session` instance. If not provided, it is inferred via
       :func:`~shiny.session.get_current_session`.

    Note
    ----
    {note}

    See Also
    -------
    ~shiny.ui.input_select
    """

    session = require_active_session(session)

    if choices is None:
        options = None
    else:
        option_tags = _render_choices(_normalize_choices(choices), selected)
        # Typing problem due to a bug in pylance:
        # https://github.com/microsoft/pylance-release/issues/2377
        options = session._process_ui(option_tags)["html"]  # type: ignore

    msg = {
        "label": label,
        "options": options,
        "selected": selected,
    }
    session.send_input_message(id, drop_none(msg))


# -----------------------------------------------------------------------------
# input_slider.py
# -----------------------------------------------------------------------------
@doc_format(note=_note)
@add_example()
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
        Only used if the slider values are :func:`~datetime.date` or
        :func:`~datetime.datetime` objects. A time format string, to be passed to the
        Javascript strftime library. See https://github.com/samsonjs/strftime for more
        details. For Dates, the default is "%F" (like "2015-07-01"), and for Datetimes,
        the default is "%F %T" (like "2015-07-01 15:32:10").
    timezone
        Only used if the values are :func:`~datetime.datetime` objects. A string
        specifying the time zone offset for the displayed times, in the format "+HHMM"
        or "-HHMM". If ``None`` (the default), times will be displayed in the browser's
        time zone. The value "+0000" will result in UTC time.
    session
        A :class:`~shiny.Session` instance. If not provided, it is inferred via
       :func:`~shiny.session.get_current_session`.

    Note
    ----
    {note}

    See Also
    -------
    ~shiny.ui.input_slider
    """

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
@doc_format(note=_note)
@add_example()
def update_text(
    id: str,
    *,
    label: Optional[str] = None,
    value: Optional[str] = None,
    placeholder: Optional[str] = None,
    session: Optional[Session] = None,
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
    session
        A :class:`~shiny.Session` instance. If not provided, it is inferred via
       :func:`~shiny.session.get_current_session`.

    Note
    ----
    {note}

    See Also
    -------
    ~shiny.ui.input_text
    """

    session = require_active_session(session)
    msg = {"label": label, "value": value, "placeholder": placeholder}
    session.send_input_message(id, drop_none(msg))


update_text_area = update_text
update_text_area.__doc__ = update_text.__doc__


# -----------------------------------------------------------------------------
# navs.py
# -----------------------------------------------------------------------------

# TODO: we should probably provide a nav_select() alias for this as well
@doc_format(note=_note)
@add_example()
def update_navs(
    id: str, selected: Optional[str] = None, session: Optional[Session] = None
) -> None:
    """
    Change the value of a navs container on the client.

    Parameters
    ----------
    id
        An input id.
    selected
        The values that should be initially selected, if any.
    session
        A :class:`~shiny.Session` instance. If not provided, it is inferred via
       :func:`~shiny.session.get_current_session`.

    Note
    ----
    {note}

    See Also
    -------
    ~shiny.ui.navset_tab
    ~shiny.ui.navset_pill
    ~shiny.ui.page_navbar
    """

    session = require_active_session(session)
    msg = {"value": selected}
    session.send_input_message(id, drop_none(msg))
