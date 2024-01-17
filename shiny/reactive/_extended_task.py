from __future__ import annotations

import asyncio
from typing import (
    Awaitable,
    Callable,
    Generic,
    Literal,
    Optional,
    TypeVar,
    cast,
    overload,
)

from .._docstring import add_example
from .._namespaces import resolve_id
from .._typing_extensions import ParamSpec
from .._utils import is_async_callable
from .._validation import req
from ._core import Context, flush, lock
from ._reactives import Value, effect, isolate

P = ParamSpec("P")
R = TypeVar("R")


__all__ = (
    "Status",
    "ExtendedTask",
    "extended_task",
)

Status = Literal["initial", "running", "success", "error", "cancelled"]


class DenialContext(Context):
    """
    A context that denies all requests to read reactive sources. We use this to ensure
    that code run outside of reactive.lock doesn't inadvertedly read reactive sources.
    """

    def on_invalidate(self, func: Callable[[], None]) -> None:
        raise RuntimeError(
            "You're not allowed to read reactive sources from inside a Extended Task. "
            "Instead, read the reactive sources before calling the extended task, and "
            "pass them in as function arguments."
        )


class ExtendedTask(Generic[P, R]):
    def __init__(self, func: Callable[P, Awaitable[R]]):
        if not is_async_callable(func):
            raise TypeError("ExtendedTask can only be used with async functions")
        self._func = func
        self._task: Optional[asyncio.Task[R]] = None

        self.status: Value[Status] = Value("initial")
        """
        Reactive value that tracks the current status of the task. The value will be one
        of "initial", "running", "success", "error", or "cancelled".
        """

        self.value: Value[R] = Value()
        """
        Reactive value that tracks the result of the task, if the current status is
        "success". If the status is not "success", the value will be unset, and a silent
        exception will be raised if you try to read it. Calling code should generally
        not read this value directly, but instead use the `result()` method, which is
        designed to behave correctly regardless of the current status.
        """

        self.error: Value[BaseException] = Value()
        """
        Reactive value that tracks the error raised by the task, if the current status
        is "error". If the status is not "error", the value will be unset, and a silent
        exception will be raised if you try to read it. Calling code should generally
        not read this value directly, but instead use the `result()` method, which is
        designed to behave correctly regardless of the current status.
        """

        # If invoked while a previous invocation is still running, we queue up.
        self._invocation_queue: list[Callable[[], None]] = []

    def cancel(self) -> None:
        """
        Cancel the current invocation, if any. If there are pending invocations, cancel
        those too.
        """
        self._invocation_queue.clear()
        if self._task is not None:
            self._task.cancel()

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> None:
        self.invoke(*args, **kwargs)

    def invoke(self, *args: P.args, **kwargs: P.kwargs) -> None:
        """
        Request execution of the slow computation. If there's already a computation in
        progress, this will queue up the new invocation to be run after the current one.
        The arguments to this function are passed to the underlying function.

        Returns
        -------
        :
            Immediately returns `None`. The results of the computation will be available
            via the `result()` method.
        """
        with isolate():
            if self.status() == "running" or len(self._invocation_queue) > 0:
                self._invocation_queue.append(lambda: self._invoke(*args, **kwargs))
            else:
                self._invoke(*args, **kwargs)

    def _invoke(self, *args: P.args, **kwargs: P.kwargs) -> None:
        """
        Internal implementation of `invoke()`. The public wrapper protects this method
        from being called while a previous invocation is still running.
        """
        assert self._task is None

        self.status.set("running")
        self.value.unset()
        self.error.unset()
        self._task = asyncio.create_task(self._execution_wrapper(*args, **kwargs))
        self._task.add_done_callback(self._done_callback)

    async def _execution_wrapper(self, *args: P.args, **kwargs: P.kwargs) -> R:
        """
        Wraps the user code in a context that denies access to reactive sources.
        """
        with DenialContext()():
            return await self._func(*args, **kwargs)

    def _done_callback(self, task: asyncio.Task[R]) -> None:
        """
        Several things must happen when a task finishes:
        1. Update the status and value/error.
        2. Reactive flush, so that reactive dependencies can move forward.
        3. If there are queued up invocations, run the next one.
        """

        if self._task is not task:
            return  # This task was cancelled, and a new one was started

        # If the task failed, save the error in self.error.
        # If it succeeded, save the result in self.value.
        self._task = None

        async def _impl():
            async with lock():
                if task.cancelled():
                    self.status.set("cancelled")
                elif task.exception() is not None:
                    self.error.set(cast(BaseException, task.exception()))
                    self.status.set("error")
                else:
                    self.value.set(task.result())
                    self.status.set("success")

                await flush()

                if len(self._invocation_queue) > 0:
                    next_invocation = self._invocation_queue.pop(0)
                    next_invocation()
                    await flush()

        asyncio.create_task(_impl())

    def result(self) -> R:
        """
        Call from a reactive context (e.g. a render function,
        :func:`~shiny.reactive.calc`, or :func:`~shiny.reactive.effect`) to get the
        result of the computation.

        * If the computation has finished successfully, the result will be returned.

        * If the computation has finished with an error, the error will be raised.

        * If the computation has never run, or the most recent run was cancelled, a
          silent exception will be raised that will clear any downstream outputs.

        * If the computation is currently running, a special type of silent exception
          will be raised that will cause the output to visually reflect that calculation
          is in progress.
        """

        if self.status() == "success":
            return self.value.get()
        elif self.status() == "error":
            raise self.error.get()
        elif self.status() == "running":
            req(False, cancel_output="progress")
            # Will never get here, but make type checker happy
            return self.value.get()
        else:  # init, cancelled
            req(False)
            # Will never get here, but make type checker happy
            return self.value.get()

    def bind_task_button(self, id: str) -> None:
        """
        Bind the extended task to the :func:`~shiny.ui.input_task_button` with the given
        ID, so that the button will go into a "busy" state for as long as the task is
        running.

        Please note the following:

        * This method does not actually create a button. It only binds the task to a
          task button that already exists in the app.

        * This method does not automatically cause button presses to invoke the extended
          task; you still need to use a :func:`~shiny.reactive.effect` (and probably
          :func:`~shiny.reactive.event` as well) to invoke the task when the button is
          pressed.

        * You cannot bind the same task button to multiple extended tasks. If you
          attempt to do so, any bound task that completes first will cause the button to
          return to the "ready" state, even if the other task is still running. (You
          can, however, bind multiple task buttons to the same extended task if you
          choose to.)

        Parameters
        ----------
        id
            ID of the task button to bind to.
        """

        # These imports have to go here, in order to avoid a circular dependency
        from ..session import get_current_session
        from ..ui import update_task_button

        session = get_current_session()
        if session is None:
            # We may be in Shiny Express UI rendering mode, where there is no session
            return

        id = resolve_id(id)

        @effect(priority=1000)
        def effect_sync_button():
            if self.status() == "running":
                update_task_button(id, state="busy")
            else:
                update_task_button(id, state="ready")


@overload
def extended_task() -> Callable[[Callable[P, Awaitable[R]]], ExtendedTask[P, R]]:
    ...


@overload
def extended_task(func: Callable[P, Awaitable[R]]) -> ExtendedTask[P, R]:
    ...


@add_example()
def extended_task(
    func: Optional[Callable[P, Awaitable[R]]] = None
) -> ExtendedTask[P, R] | Callable[[Callable[P, Awaitable[R]]], ExtendedTask[P, R]]:
    """
    Decorator to mark an async function as a slow computation. This will cause the
    function to be run in a background asyncio task, and the results will be available
    via the :class:`~shiny.reactive.ExtendedTask` object returned by the decorator.

    Unlike normal async render functions, effects, and calcs, `extended_task` async
    computations do not block Shiny reactive processing from proceeding. This means that
    they can be used to perform long-running tasks without freezing the session that
    owns them, nor other sessions.

    However, this also means that they cannot access reactive sources. This is because
    processing of inputs and reactivity is not blocked, and so the reactive sources may
    change while the computation is running, which is almost never the desired behavior.
    If any reactive sources are needed by the computation, the decorated function must
    take them as parameters, and the resulting `ExtendedTask` object must be invoked
    with the corresponding arguments.

    Parameters
    ----------
    func
        The function to decorate. It must be ``async``. It can take any parameters and
        return any value (including None).

    Returns
    -------
    :
        An ``ExtendedTask`` object that can be used to check the status of the
        computation and retrieve the result.
    """

    def decorator(func: Callable[P, Awaitable[R]]) -> ExtendedTask[P, R]:
        return ExtendedTask(func)

    if func is not None:
        return decorator(func)
    else:
        return decorator
