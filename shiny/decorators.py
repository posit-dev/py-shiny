import functools
from typing import TypeVar, Callable, List, Awaitable, Any, Union, cast

from .input_handlers import ActionButtonValue
from .reactives import isolate
from .validation import req
from .utils import is_async_callable, run_coro_sync


TBA = TypeVar("TBA", bound=Any)


def event(
    *args: Union[Callable[[], object], Callable[[], Awaitable[object]]],
    ignore_none: bool = True,
    ignore_init: bool = False,
) -> Callable[[Callable[[], TBA]], Callable[[], TBA]]:
    def decorator(user_fn: Callable[[], TBA]) -> Callable[[], TBA]:

        initialized = False

        async def trigger() -> None:
            vals: List[object] = []
            for arg in args:
                if is_async_callable(arg):
                    arg = cast(Callable[[], Awaitable[object]], arg)
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
            async def new_user_fn() -> TBA:
                await trigger()
                with isolate():
                    return await user_fn()

        elif any(map(is_async_callable, args)):

            raise TypeError(
                "When decorating a syncronous function with @event(), all arguments"
                + "to @event() must be syncronous functions."
            )

        else:

            @functools.wraps(user_fn)
            def new_user_fn() -> TBA:
                run_coro_sync(trigger())
                with isolate():
                    return user_fn()

        return new_user_fn

    return decorator


def _is_none_event(val: object) -> bool:
    return val is None or (isinstance(val, ActionButtonValue) and val == 0)
