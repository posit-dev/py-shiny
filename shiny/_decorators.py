import functools
from typing import TypeVar, Callable, List, Awaitable, Union

from ._docstring import add_example
from .input_handler import ActionButtonValue
from .reactive import isolate
from ._validation import req
from ._utils import is_async_callable, run_coro_sync


T = TypeVar("T")


@add_example()
def event(
    *args: Union[Callable[[], object], Callable[[], Awaitable[object]]],
    ignore_none: bool = True,
    ignore_init: bool = False,
) -> Callable[[Callable[[], T]], Callable[[], T]]:
    """
    Mark a function to react only when an "event" occurs.

    Shiny's reactive programming framework is primarily designed for calculated values
    (:func:`~shiny.reactive.Calc`) and side-effect-causing actions
    (:func:`~shiny.reactive.Effect`) that respond to **any** of their inputs changing.
    That's often what is desired in Shiny apps, but not always: sometimes you want to
    wait for a specific action to be taken from the user, like clicking an
    :func:`~shiny.ui.input_action_button`, before calculating or taking an action. A
    reactive value (or function) which triggers other calculation or action in this way
    is called an event.

    These situations demand a more imperative, "event handling" style of programming,
    which ``@event()`` provides. It does this by using the
    :func:`~shiny.reactive.isolate` primitive under-the-hood to essentially "limit" the
    set of reactive dependencies to those in ``args``.

    Parameters
    ----------
    args
        One or more callables that represent the event; most likely this will be a
        reactive input value linked to a :func:`~shiny.ui.input_action_button` or
        similar (e.g., ``input.click``), but it can also be a (reactive or non-reactive)
        function that returns a value.
    ignore_none
        Whether to ignore the event if the value is ``None`` or ``0``.
    ignore_init
        If ``False``, the event trigger on the first run.

    Returns
    -------
    A decorator that marks a function as an event handler.

    Tip
    ----
    This decorator must be applied before the relevant reactivity decorator (i.e.,
    ``@event`` must be applied before ``@reactive.Effect``, ``@reactive.Calc``,
    ``@render.ui``, etc).
    """

    if any([not callable(arg) for arg in args]):
        raise TypeError(
            "All objects passed to event decorator must be callable.\n"
            + "If you are calling `@event(f())`, try calling `@event(f)` instead."
        )

    def decorator(user_fn: Callable[[], T]) -> Callable[[], T]:

        initialized = False

        async def trigger() -> None:
            vals: List[object] = []
            for arg in args:
                if is_async_callable(arg):
                    v = await arg()
                else:
                    v = arg()
                vals.append(v)

            nonlocal initialized
            if ignore_init and not initialized:
                initialized = True
                req(False)
            if ignore_none and all(map(_is_none_event, vals)):
                req(False)

        if is_async_callable(user_fn):

            @functools.wraps(user_fn)
            # Impossible to specify a return type here; we know T is
            # Awaitable[something] but I don't think there's a way to refer to the
            # `something`
            async def new_user_async_fn():
                await trigger()
                with isolate():
                    return await user_fn()

            return new_user_async_fn  # type: ignore

        elif any([is_async_callable(arg) for arg in args]):
            raise TypeError(
                "When decorating a synchronous function with @event(), all arguments"
                + "to @event() must be synchronous functions."
            )

        else:

            @functools.wraps(user_fn)
            def new_user_fn() -> T:
                run_coro_sync(trigger())
                with isolate():
                    return user_fn()

            return new_user_fn

    return decorator


def _is_none_event(val: object) -> bool:
    return val is None or (isinstance(val, ActionButtonValue) and val == 0)
