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

from .._namespaces import resolve_id
from .._typing_extensions import ParamSpec
from .._validation import req
from ._core import Context, flush, lock
from ._reactives import Value, effect, isolate

P = ParamSpec("P")
R = TypeVar("R")

Status = Literal["initial", "running", "success", "error", "cancelled"]


class DenialContext(Context):
    """
    A context that denies all requests to read reactive sources. We use this to ensure
    that code run outside of reactive.lock doesn't inadvertedly read reactive sources.
    """

    def on_invalidate(self, func: Callable[[], None]) -> None:
        raise RuntimeError(
            "You're not allowed to read reactive sources from inside a ExtendedTask"
        )


class ExtendedTask(Generic[P, R]):
    # TODO: What to do when __call__ is called while a previous computation is still
    # running? Should we cancel the previous one? Should we queue up the new one? Should
    # we throw an error?

    def __init__(self, func: Callable[P, Awaitable[R]]):
        self.func = func
        self.task: Optional[asyncio.Task[R]] = None

        # init, running, success, error
        self.status: Value[Status] = Value("initial")
        self.value: Value[R] = Value()
        self.error: Value[BaseException] = Value()

        # If invoked while a previous invocation is still running, we queue up.
        self._invocation_queue: list[Callable[[], None]] = []

    def cancel(self) -> None:
        """
        Cancel the current invocation, if any. If there are running invocations, cancel
        those too.
        """
        self._invocation_queue.clear()
        if self.task is not None:
            self.task.cancel()

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
        assert self.task is None

        self.status.set("running")
        self.value.unset()
        self.error.unset()
        self.task = asyncio.create_task(self._execution_wrapper(*args, **kwargs))
        self.task.add_done_callback(self._done_callback)

    async def _execution_wrapper(self, *args: P.args, **kwargs: P.kwargs) -> R:
        """
        Wraps the user code in a context that denies access to reactive sources.
        """
        with DenialContext()():
            return await self.func(*args, **kwargs)

    def _done_callback(self, task: asyncio.Task[R]) -> None:
        """
        Several things must happen when a task finishes:
        1. Update the status and value/error.
        2. Reactive flush, so that reactive dependencies can move forward.
        3. If there are queued up invocations, run the next one.
        """

        if self.task is not task:
            return  # This task was cancelled, and a new one was started

        # If the task failed, save the error in self.error.
        # If it succeeded, save the result in self.value.
        self.task = None

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


def extended_task(
    func: Optional[Callable[P, Awaitable[R]]] = None
) -> ExtendedTask[P, R] | Callable[[Callable[P, Awaitable[R]]], ExtendedTask[P, R]]:
    """
    Decorator to mark an async function as a slow computation. This will cause the
    function to be run in a background task, and the results will be available via the
    `ExtendedTask` object returned by the decorator.

    Unlike normal async render functions, effects, and calcs, `extended_task` async
    computations do not block the main thread. This means that they can be used to
    perform long-running tasks without blocking the UI.

    However, this also means that they cannot access reactive sources. This is because
    the main thread is not blocked, and so the reactive sources may change while the
    computation is running. If any reactive sources are needed by the computation, they
    must be passed in as arguments to the function.

    Parameters
    ----------
    func : Callable[[P], Awaitable[R]]
        The function to decorate. It can take any parameters and return any value
        (including None).

    Returns
    -------
    :
        A `ExtendedTask` object that can be used to check the status of the
        computation and retrieve the result.
    """

    def decorator(func: Callable[P, Awaitable[R]]) -> ExtendedTask[P, R]:
        return ExtendedTask(func)

    if func is not None:
        return decorator(func)
    else:
        return decorator
