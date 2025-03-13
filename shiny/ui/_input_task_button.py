from __future__ import annotations

__all__ = ("input_task_button",)

from functools import partial
from typing import Callable, Optional, TypeVar, cast, overload

from htmltools import HTML, Tag, TagAttrValue, TagChild, css, tags

from .._docstring import add_example
from .._typing_extensions import ParamSpec
from ..module import resolve_id
from ..reactive._extended_task import ExtendedTask
from ..reactive._reactives import effect
from ..types import MISSING, MISSING_TYPE
from ._html_deps_py_shiny import spin_dependency
from ._html_deps_shinyverse import components_dependencies

P = ParamSpec("P")
R = TypeVar("R")

spinner_icon = """<svg class="py-shiny-spin" viewBox="0 0 512 512" preserveAspectRatio="none" aria-hidden="true" role="img" style="fill:currentColor;height:1em;width:1.0em;margin-left:auto;margin-right:0.2em;position:relative;vertical-align:-0.125em;font-size:inherit;overflow:visible;">
  <path d="M142.9 142.9c62.2-62.2 162.7-62.5 225.3-1L327 183c-6.9 6.9-8.9 17.2-5.2 26.2s12.5 14.8 22.2 14.8H463.5c0 0 0 0 0 0H472c13.3 0 24-10.7 24-24V72c0-9.7-5.8-18.5-14.8-22.2s-19.3-1.7-26.2 5.2L413.4 96.6c-87.6-86.5-228.7-86.2-315.8 1C73.2 122 55.6 150.7 44.8 181.4c-5.9 16.7 2.9 34.9 19.5 40.8s34.9-2.9 40.8-19.5c7.7-21.8 20.2-42.3 37.8-59.8zM16 312v7.6 .7V440c0 9.7 5.8 18.5 14.8 22.2s19.3 1.7 26.2-5.2l41.6-41.6c87.6 86.5 228.7 86.2 315.8-1c24.4-24.4 42.1-53.1 52.9-83.7c5.9-16.7-2.9-34.9-19.5-40.8s-34.9 2.9-40.8 19.5c-7.7 21.8-20.2 42.3-37.8 59.8c-62.2 62.2-162.7 62.5-225.3 1L185 329c6.9-6.9 8.9-17.2 5.2-26.2s-12.5-14.8-22.2-14.8H48.4h-.7H40c-13.3 0-24 10.7-24 24z"></path>
</svg>"""


@add_example(ex_dir="../api-examples/extended_task")
def input_task_button(
    id: str,
    label: TagChild,
    *args: TagChild,
    icon: TagChild = None,
    label_busy: TagChild = "Processing...",
    icon_busy: TagChild | MISSING_TYPE = MISSING,
    width: Optional[str] = None,
    type: Optional[str] = "primary",
    auto_reset: bool = True,
    **kwargs: TagAttrValue,
) -> Tag:
    """
    Creates a button for launching longer-running operations.

    Its value is initially zero, and increments by one each time it is pressed. It is
    similar to :func:`~shiny.ui.input_action_button`, except it prevents the user from
    clicking when its operation is already in progress.

    Upon click, it automatically displays a customizable progress message and disables
    itself; and after the server has dealt with whatever reactivity is triggered from
    the click, the button automatically resets to its original appearance and re-enables
    itself.

    In some advanced use cases, it may be necessary to keep a task button in its busy
    state even after the normal reactive processing has completed. Calling
    :func:`~shiny.ui.update_task_button(id, state = "busy")` from the server will opt
    out of any currently pending reset for a specific task button. After doing so, the
    button can be re-enabled by calling ``update_task_button(id, state = "ready")``
    after each click's work is complete.

    You can also pass an explicit ``auto_reset = FALSE`` to ``input_task_button()``,
    which means that button will _never_ be automatically re-enabled and will require
    ``update_task_button(id, state = "ready")`` to be called each time.

    Note that, as a general rule, Shiny's ``update`` family of functions do not take
    effect at the instant that they are called, but are held until the end of the
    current reactive cycle. So if you have many different reactive calculations and
    outputs, you don't have to be too careful about when you call
    ``update_task_button(id, state = "ready")``, as the button on the client will not
    actually re-enable until the same moment that all of the updated outputs
    simultaneously sent to the client.

    Parameters
    ----------
    id
        An input id.
    label
        A button label.
    *args
        [Experimental] Can be used to add additional states besides "ready" and "busy".
        Pass a :func:`~shiny.ui.tags.span` with ``slot="state_name"`` for each new
        state, and call :func:`~shiny.ui.update_task_button` with ``state="state_name"``
        to switch the button to that state.
    icon
        An icon to appear inline with the button/link.
    label_busy
        A label to appear when the button is busy.
    icon_busy
        An icon to appear inline with the button/link when the button is busy.
    width
        The CSS width, e.g. '400px', or '100%'
    type
        One of the Bootstrap theme colors ('primary', 'default', 'secondary', 'success',
        'danger', 'warning', 'info', 'light', 'dark'), or None to leave off the
        Bootstrap-specific button CSS classes. Defaults to 'primary'.
    auto_reset
        Whether to automatically reset the button to "ready" after the task completes.
        If False, the button will remain in the "busy" state until
        :func:`~shiny.ui.update_task_button` is called with ``state="ready"``. Also note
        that even if ``auto_reset=True``, calling :func:`~shiny.ui.update_task_button`
        with ``state="busy"`` will prevent the button from automatically resetting.
    **kwargs
        Attributes to be applied to the button.

    Returns
    -------
    :
        A UI element

    Notes
    ------
    ::: {.callout-note title="Server value"}
    An integer representing the number of clicks.
    :::

    See Also
    --------
    * :func:`~shiny.ui.update_task_button`
    * :func:`~shiny.ui.input_action_button`
    * :func:`~shiny.reactive.event`
    """

    if "_add_ws" not in kwargs:
        kwargs["_add_ws"] = True

    if icon_busy is MISSING:
        icon_busy = HTML(spinner_icon)

    css_class = "bslib-task-button" + f" btn btn-{type}" if type is not None else ""

    return tags.button(
        {"class": css_class, "style": css(width=width), "data-auto-reset": auto_reset},
        Tag(
            "bslib-switch-inline",
            tags.span(
                icon,
                " " if icon is not None else None,
                label,
                slot="ready",
            ),
            tags.span(
                cast(TagChild, icon_busy),
                " " if icon_busy is not None else None,
                label_busy,
                slot="busy",
            ),
            *args,
            case="ready",
        ),
        components_dependencies(),
        spin_dependency(),
        id=resolve_id(id),
        type="button",
        **kwargs,
    )


@overload
def bind_task_button(
    *, button_id: str
) -> Callable[[ExtendedTask[P, R]], ExtendedTask[P, R]]: ...


@overload
def bind_task_button(
    task: ExtendedTask[P, R], *, button_id: str
) -> ExtendedTask[P, R]: ...


def bind_task_button(
    task: ExtendedTask[P, R] | None = None, *, button_id: str
) -> ExtendedTask[P, R] | Callable[[ExtendedTask[P, R]], ExtendedTask[P, R]]:
    """
    Bind an :class:`ExtendedTask` to the :func:`~shiny.ui.input_task_button` with the
    given ID, so that the button will go into a "busy" state for as long as the task is
    running.

    This can be called as a function (``bind_task_button(task, button_id="btn")``) or as
    a decorator (``@bind_task_button(button_id="btn")``, placed above
    ``@extended_task``).

    Please note the following:

    * This function does not actually create a button. It only binds the task to a task
      button that already exists in the app.

    * This function does not automatically cause button presses to invoke the extended
      task; you still need to use a :func:`~shiny.reactive.effect` (and probably
      :func:`~shiny.reactive.event` as well) to invoke the task when the button is
      pressed.

    * You cannot bind the same task button to multiple extended tasks. If you attempt to
      do so, any bound task that completes will cause the button to return to the
      "ready" state, even if the other tasks are still running. (You can, however, bind
      multiple task buttons to the same extended task if you choose to.)

    Parameters
    ----------
    id
        ID of the task button to bind to.
    """

    if task is None:
        return partial(bind_task_button, button_id=button_id)

    # These imports have to go here, in order to avoid a circular dependency
    from ..session import get_current_session
    from ..ui import update_task_button

    session = get_current_session()
    if session is None:
        # We may be in Shiny Express UI rendering mode, where there is no session
        return task

    button_id = resolve_id(button_id)

    @effect(priority=1000)
    def effect_sync_button():
        if task.status() == "running":
            update_task_button(button_id, state="busy")
        else:
            update_task_button(button_id, state="ready")

    return task
