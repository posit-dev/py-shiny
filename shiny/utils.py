from typing import TYPE_CHECKING, Callable, Awaitable, TypeVar, Optional

from htmltools import tag_list

if TYPE_CHECKING:
    from .shinysession import ShinySession
import inspect
import secrets

# ==============================================================================
# Misc utility functions
# ==============================================================================
def rand_hex(bytes: int) -> str:
    """
    Creates a random hexadecimal string of size `bytes`. The length in
    characters will be bytes*2.
    """
    format_str = "{{:0{}x}}".format(bytes * 2)
    return format_str.format(secrets.randbits(bytes * 8))


# ==============================================================================
# Async-related functions
# ==============================================================================

T = TypeVar("T")


def wrap_async(fn: Callable[[], T]) -> Callable[[], Awaitable[T]]:
    """
    Wrap a synchronous function that returns T, and return an async function
    that wraps the original function.
    """

    async def fn_async() -> T:
        return fn()

    return fn_async


def is_async_callable(obj: object) -> bool:
    """
    Returns True if `obj` is an `async def` function, or if it's an object with
    a `__call__` method which is an `async def` function.
    """
    if inspect.iscoroutinefunction(obj):
        return True
    if hasattr(obj, "__call__"):
        if inspect.iscoroutinefunction(obj.__call__):  # type: ignore
            return True

    return False


# See https://stackoverflow.com/a/59780868/412655 for an excellent explanation
# of how this stuff works.
# For a more in-depth explanation, see
# https://snarky.ca/how-the-heck-does-async-await-work-in-python-3-5/.
def run_coro_sync(coro: Awaitable[T]) -> T:
    """
    Run a coroutine that is in fact synchronous. Given a coroutine (which is
    returned by calling an `async def` function), this function will run the
    coroutine for one iteration. If the coroutine completes, then return the
    value. If it does not complete, then it will throw a `RuntimeError`.

    What it means to be "in fact synchronous": the coroutine must not yield
    control to the event loop. A coroutine may have an `await` expression in it,
    and that may call another function that has an `await`, but the chain will
    only yield control if a `yield` statement bubbles through `await`s all the
    way up. For example, `await asyncio.sleep(0)` will have a `yield` which
    bubbles up to the next level. Note that a `yield` in a generator used the
    regular way (not with `await`) will not bubble up, since it is not awaited
    on.
    """
    if not inspect.iscoroutine(coro):
        raise TypeError("run_coro_sync requires a Coroutine object.")

    try:
        coro.send(None)
    except StopIteration as e:
        return e.value

    raise RuntimeError(
        "async function yielded control; it did not finish in one iteration."
    )


def process_deps(ui, s: Optional["ShinySession"] = None):
    if s is None:
        from .shinysession import get_current_session

        s = get_current_session()

    from .connmanager import create_web_dependency

    def register_dep(d):
        return create_web_dependency(s._app._conn_manager._fastapi_app, d)

    if not isinstance(ui, tag_list):
        ui = tag_list(ui)
    res = ui.render(process_dep=register_dep)
    return res
