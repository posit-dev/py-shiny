import functools
from typing import TypeVar, Callable, List, Awaitable, Union

from .reactive import isolate
from ._validation import req
from ._utils import is_async_callable, run_coro_sync


T = TypeVar("T")


def event(
    *args: Union[Callable[[], object], Callable[[], Awaitable[object]]],
    ignore_init: bool = False,
) -> Callable[[Callable[[], T]], Callable[[], T]]:

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

        if is_async_callable(user_fn):

            @functools.wraps(user_fn)
            async def new_user_fn() -> T:
                await trigger()
                with isolate():
                    return await user_fn()

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
