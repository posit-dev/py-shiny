from __future__ import annotations

__all__ = ("input_submit_textarea", "update_submit_textarea")

import copy
from typing import Literal, Optional

from htmltools import Tag, TagAttrValue, TagChild, css, div, span, tags

from .._docstring import add_example
from .._utils import drop_none
from ..bookmark import restore_input
from ..module import resolve_id
from ..session import Session, require_active_session
from ._html_deps_shinyverse import components_dependencies
from ._input_task_button import input_task_button
from ._utils import shiny_input_label


@add_example()
def input_submit_textarea(
    id: str,
    label: TagChild = None,
    *,
    placeholder: Optional[str] = None,
    value: str = "",
    width: str = "min(680px, 100%)",
    rows: int = 1,
    button: Optional[Tag] = None,
    toolbar: TagChild | TagAttrValue = None,
    submit_key: Literal["enter+modifier", "enter"] = "enter+modifier",
    **kwargs: TagAttrValue,
) -> Tag:
    """
    Create a textarea input control with explicit submission.

    Creates a textarea input where users can enter multi-line text and submit
    their input using a dedicated button or keyboard shortcut. This control is
    ideal when you want to capture finalized input, rather than reacting to every
    keystroke, making it useful for chat boxes, comments, or other scenarios
    where users may compose and review their text before submitting.

    Parameters
    ----------
    id
        The input ID.
    label
        The label to display above the input control. If `None`, no label is displayed.
    placeholder
        The placeholder text to display when the input is empty. This can be used to
        provide a hint or example of the expected input.
    value
        The initial input text. Note that, unlike :func:`~shiny.ui.input_text_area`,
        this won't set a server-side value until the value is explicitly submitted.
    width
        Any valid CSS unit (e.g., `width="100%"`).
    rows
        The number of rows (i.e., height) of the textarea. This essentially sets the
        minimum height -- the textarea can grow taller as the user enters more text.
    button
        A :class:`~htmltools.Tag` element to use for the submit button. It's recommended
        that this be an :func:`~shiny.ui.input_task_button` since it will automatically
        provide a busy indicator (and disable) until the next flush occurs. Note also
        that if the submit button launches an :class:`~shiny.reactive.ExtendedTask`,
        this button can also be bound to the task (:func:`~shiny.ui.bind_task_button`)
        and/or manually updated for more accurate progress reporting
        (:func:`~shiny.ui.update_task_button`).
    toolbar
        UI elements to include alongside the submit button (e.g., help text, links, etc.).
    submit_key
        A string indicating what keyboard event should trigger the submit button.
        The default is `"enter+modifier"`, which requires the user to hold down
        Ctrl (or Cmd on Mac) before pressing Enter to submit. This helps prevent
        accidental submissions. To allow submission with just the Enter key, use
        `"enter"`. In this case, the user can still insert new lines using
        Shift+Enter or Alt+Enter.
    **kwargs
        Additional attributes to apply to the underlying `<textarea>` element
        (e.g., spellcheck, autocomplete, etc).

    Returns
    -------
    :
        A textarea input control that can be added to a UI definition.

    Notes
    ------
    ::: {.callout-note title="Server value"}
    A character string containing the user's text input.

    **Important:** The server isn't sent a value until the user explicitly submits the
    input. This means that reading the input value results in a
    :class:`~shiny.types.SilentException` until the user actually submits input. After
    that, the server will only see updated values when the user submits the input again.
    For this reason, if you want to avoid the exception and return a value, check for
    the input ID using `if "input_id" in input` before reading the value. See the
    examples for a demonstration.
    :::

    See Also
    --------
    * :func:`~shiny.ui.update_submit_textarea`
    * :func:`~shiny.ui.input_task_button`
    * :func:`~shiny.ui.input_text_area`
    """
    resolved_id = resolve_id(id)
    value = restore_input(resolved_id, default=value)
    if not isinstance(value, str):
        raise TypeError("`value` must be a string")

    needs_modifier = submit_key == "enter+modifier"

    if button is None:
        button = input_task_button(
            id=f"{resolved_id}_submit",
            class_="btn-sm",
            label=span("\u23ce", class_="bslib-submit-key"),
            icon="Submit",
            label_busy=div(
                span("Processing...", class_="visually-hidden"),
                class_="spinner-border spinner-border-sm ms-2",
                role="status",
            ),
            icon_busy="Submit",
            title="Press Enter to Submit",
            aria_label="Press Enter to Submit",
        )

    if not is_button_tag(button):
        raise TypeError("`button` must be a button tag")

    button2 = copy.copy(button)
    button2.add_class("bslib-submit-textarea-btn")

    return div(
        {
            "class": "bslib-input-submit-textarea shiny-input-container bslib-mb-spacing",
            "style": css(width=width),
        },
        shiny_input_label(resolved_id, label),
        div(
            tags.textarea(
                value,
                {"class": "form-control", "style": css(width="100%")},
                id=resolved_id,
                placeholder=placeholder,
                data_needs_modifier="" if needs_modifier else None,
                rows=rows,
                **kwargs,
            ),
            tags.footer(
                div(toolbar, class_="bslib-toolbar"),
                button2,
            ),
            class_="bslib-submit-textarea-container",
        ),
        components_dependencies(),
    )


def is_button_tag(x: object) -> bool:
    if not isinstance(x, Tag):
        return False
    return x.name == "button" or x.attrs.get("type") == "button"


@add_example()
def update_submit_textarea(
    id: str,
    *,
    value: Optional[str] = None,
    placeholder: Optional[str] = None,
    label: Optional[TagChild] = None,
    submit: bool = False,
    focus: bool = False,
    session: Optional[Session] = None,
) -> None:
    """
    Update a submit textarea input on the client.

    Parameters
    ----------
    id
        The input ID.
    value
        The value to set the user input to.
    placeholder
        The placeholder text for the user input.
    label
        The label for the input.
    submit
        Whether to automatically submit the text for the user. Requires `value`.
    focus
        Whether to move focus to the input element. Requires `value`.
    session
        A :class:`~shiny.Session` instance. If not provided, it is inferred via
        :func:`~shiny.session.get_current_session`.

    See Also
    --------
    * :func:`~shiny.ui.input_submit_textarea`
    """
    if value is None and (submit or focus):
        raise ValueError(
            "An input `value` must be provided when `submit` or `focus` are `True`."
        )

    session = require_active_session(session)

    msg = {
        "value": value,
        "placeholder": placeholder,
        "label": session._process_ui(label) if label is not None else None,
        "submit": submit,
        "focus": focus,
    }

    session.send_input_message(id, drop_none(msg))
