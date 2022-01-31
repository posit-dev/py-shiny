"""Reactive components"""

__all__ = (
    "ReactiveVal",
    "ReactiveValues",
    "Reactive",
    "ReactiveAsync",
    "reactive",
    "reactive_async",
    "Observer",
    "ObserverAsync",
    "observe",
    "observe_async",
    "isolate",
)

from typing import (
    TYPE_CHECKING,
    Optional,
    Callable,
    Awaitable,
    TypeVar,
    Union,
    Generic,
    Any,
    overload,
)
import typing
import inspect
import warnings
import traceback

from .reactcore import Context, Dependents, ReactiveWarning
from . import reactcore
from . import utils
from .types import MISSING, MISSING_TYPE
from .validation import SilentException

if TYPE_CHECKING:
    from .shinysession import ShinySession

T = TypeVar("T")

# ==============================================================================
# ReactiveVal and ReactiveValues
# ==============================================================================
class ReactiveVal(Generic[T]):
    def __init__(self, value: T) -> None:
        self._value: T = value
        self._dependents: Dependents = Dependents()

    @overload
    def __call__(self) -> T:
        ...

    @overload
    def __call__(self, value: T) -> bool:
        ...

    def __call__(self, value: Union[MISSING_TYPE, T] = MISSING) -> Union[T, bool]:
        if isinstance(value, MISSING_TYPE):
            return self.get()
        else:
            return self.set(value)

    def get(self) -> T:
        self._dependents.register()
        return self._value

    def set(self, value: T) -> bool:
        if self._value is value:
            return False

        self._value = value
        self._dependents.invalidate()
        return True


class ReactiveValues:
    def __init__(self, **kwargs: object) -> None:
        self._map: dict[str, ReactiveVal[Any]] = {}
        for key, value in kwargs.items():
            self._map[key] = ReactiveVal(value)

    def __setitem__(self, key: str, value: object) -> None:
        if key in self._map:
            self._map[key](value)
        else:
            self._map[key] = ReactiveVal(value)

    def __getitem__(self, key: str) -> Any:
        # Auto-populate key if accessed but not yet set. Needed to take reactive
        # dependencies on input values that haven't been received from client
        # yet.
        if key not in self._map:
            self._map[key] = ReactiveVal(None)

        return self._map[key]()

    def __delitem__(self, key: str) -> None:
        del self._map[key]


# ==============================================================================
# Reactive
# ==============================================================================
class Reactive(Generic[T]):
    def __init__(
        self,
        func: Callable[[], T],
        *,
        session: Union[MISSING_TYPE, "ShinySession", None] = MISSING,
    ) -> None:
        if inspect.iscoroutinefunction(func):
            raise TypeError("Reactive requires a non-async function")

        self._func: Callable[[], Awaitable[T]] = utils.wrap_async(func)
        self._is_async: bool = False

        self._dependents: Dependents = Dependents()
        self._invalidated: bool = True
        self._running: bool = False
        self._most_recent_ctx_id: int = -1
        self._ctx: Optional[Context] = None
        self._exec_count: int = 0

        self._session: Optional[ShinySession]
        # Use `isinstance(x, MISSING_TYPE)`` instead of `x is MISSING` because
        # the type checker doesn't know that MISSING is the only instance of
        # MISSING_TYPE; this saves us from casting later on.
        if isinstance(session, MISSING_TYPE):
            # If no session is provided, autodetect the current session (this
            # could be None if outside of a session).
            session = shinysession.get_current_session()
        self._session = session

        # Use lists to hold (optional) value and error, instead of Optional[T],
        # because it makes typing more straightforward. For example if
        # .get_value() simply returned self._value, self._value had type
        # Optional[T], then the return type for get_value() would have to be
        # Optional[T].
        self._value: list[T] = []
        self._error: list[Exception] = []

    def __call__(self) -> T:
        # Run the Coroutine (synchronously), and then return the value.
        # If the Coroutine yields control, then an error will be raised.
        return utils.run_coro_sync(self.get_value())

    async def get_value(self) -> T:
        self._dependents.register()

        if self._invalidated or self._running:
            await self.update_value()

        if self._error:
            raise self._error[0]

        return self._value[0]

    async def update_value(self) -> None:
        self._ctx = Context()
        self._most_recent_ctx_id = self._ctx.id

        self._ctx.on_invalidate(self._on_invalidate_cb)

        self._exec_count += 1
        self._invalidated = False

        was_running = self._running
        self._running = True

        with shinysession.session_context(self._session):
            try:
                await self._ctx.run(self._run_func, create_task=self._is_async)
            finally:
                self._running = was_running

    def _on_invalidate_cb(self) -> None:
        self._invalidated = True
        self._value.clear()  # Allow old value to be GC'd
        self._dependents.invalidate()
        self._ctx = None  # Allow context to be GC'd

    async def _run_func(self) -> None:
        self._error.clear()
        try:
            self._value.append(await self._func())
        except Exception as err:
            self._error.append(err)


class ReactiveAsync(Reactive[T]):
    def __init__(
        self,
        func: Callable[[], Awaitable[T]],
        *,
        session: Union[MISSING_TYPE, "ShinySession", None] = MISSING,
    ) -> None:
        if not inspect.iscoroutinefunction(func):
            raise TypeError("ReactiveAsync requires an async function")

        # Init the Reactive base class with a placeholder synchronous function
        # so it won't throw an error, then replace it with the async function.
        # Need the `cast` to satisfy the type checker.
        super().__init__(lambda: typing.cast(T, None), session=session)
        self._func: Callable[[], Awaitable[T]] = func
        self._is_async = True

    async def __call__(self) -> T:
        return await self.get_value()


def reactive(
    *, session: Union[MISSING_TYPE, "ShinySession", None] = MISSING
) -> Callable[[Callable[[], T]], Reactive[T]]:
    def create_reactive(fn: Callable[[], T]) -> Reactive[T]:
        return Reactive(fn, session=session)

    return create_reactive


def reactive_async(
    *, session: Union[MISSING_TYPE, "ShinySession", None] = MISSING
) -> Callable[[Callable[[], Awaitable[T]]], ReactiveAsync[T]]:
    def create_reactive_async(fn: Callable[[], Awaitable[T]]) -> ReactiveAsync[T]:
        return ReactiveAsync(fn, session=session)

    return create_reactive_async


# ==============================================================================
# Observer
# ==============================================================================
class Observer:
    def __init__(
        self,
        func: Callable[[], None],
        *,
        session: Union[MISSING_TYPE, "ShinySession", None] = MISSING,
        priority: int = 0,
    ) -> None:
        if inspect.iscoroutinefunction(func):
            raise TypeError("Observer requires a non-async function")

        self._func: Callable[[], Awaitable[None]] = utils.wrap_async(func)
        self._is_async: bool = False

        self._priority: int = priority

        self._invalidate_callbacks: list[Callable[[], None]] = []
        self._destroyed: bool = False
        self._ctx: Optional[Context] = None
        self._exec_count: int = 0

        self._session: Optional[ShinySession]
        # Use `isinstance(x, MISSING_TYPE)`` instead of `x is MISSING` because
        # the type checker doesn't know that MISSING is the only instance of
        # MISSING_TYPE; this saves us from casting later on.
        if isinstance(session, MISSING_TYPE):
            # If no session is provided, autodetect the current session (this
            # could be None if outside of a session).
            session = shinysession.get_current_session()
        self._session = session

        if self._session is not None:
            self._session.on_ended(self._on_session_ended_cb)

        # Defer the first running of this until flushReact is called
        self._create_context().invalidate()

    def _create_context(self) -> Context:
        ctx = Context()

        # Store the context explicitly in Observer object
        # TODO: More explanation here
        self._ctx = ctx

        def on_invalidate_cb() -> None:
            # Context is invalidated, so we don't need to store a reference to it
            # anymore.
            self._ctx = None

            for cb in self._invalidate_callbacks:
                cb()

            # TODO: Wrap this stuff up in a continue callback, depending on if suspended?
            ctx.add_pending_flush(self._priority)

        async def on_flush_cb() -> None:
            if not self._destroyed:
                await self.run()

        ctx.on_invalidate(on_invalidate_cb)
        ctx.on_flush(on_flush_cb)

        return ctx

    async def run(self) -> None:
        ctx = self._create_context()
        self._exec_count += 1

        with shinysession.session_context(self._session):
            try:
                await ctx.run(self._func, create_task=self._is_async)
            except SilentException:
                # It's OK for SilentException to cause an observer to stop running
                pass
            except Exception as e:
                traceback.print_exc()

                warnings.warn("Error in observer: " + str(e), ReactiveWarning)
                if self._session:
                    await self._session.unhandled_error(e)

    def on_invalidate(self, callback: Callable[[], None]) -> None:
        self._invalidate_callbacks.append(callback)

    def destroy(self) -> None:
        self._destroyed = True

        if self._ctx is not None:
            self._ctx.invalidate()

    def _on_session_ended_cb(self) -> None:
        self.destroy()


class ObserverAsync(Observer):
    def __init__(
        self,
        func: Callable[[], Awaitable[None]],
        *,
        session: Union[MISSING_TYPE, "ShinySession", None] = MISSING,
        priority: int = 0,
    ) -> None:
        if not inspect.iscoroutinefunction(func):
            raise TypeError("ObserverAsync requires an async function")

        # Init the Observer base class with a placeholder synchronous function
        # so it won't throw an error, then replace it with the async function.
        super().__init__(lambda: None, session=session, priority=priority)
        self._func: Callable[[], Awaitable[None]] = func
        self._is_async = True


def observe(
    *, priority: int = 0, session: Union[MISSING_TYPE, "ShinySession", None] = MISSING
) -> Callable[[Callable[[], None]], Observer]:
    """[summary]

    Args:
        priority : [description]. Defaults to 0.
        session : [description]. Defaults to MISSING.

    Returns:
        [description]
    """

    def create_observer(fn: Callable[[], None]) -> Observer:
        return Observer(fn, priority=priority, session=session)

    return create_observer


def observe_async(
    *, priority: int = 0, session: Union[MISSING_TYPE, "ShinySession", None] = MISSING
) -> Callable[[Callable[[], Awaitable[None]]], ObserverAsync]:
    def create_observer_async(fn: Callable[[], Awaitable[None]]) -> ObserverAsync:
        return ObserverAsync(fn, priority=priority, session=session)

    return create_observer_async


# ==============================================================================
# Miscellaneous functions
# ==============================================================================
def isolate():
    """
    Can be used via `with isolate():` or `async with isolate():` to wrap code blocks
    whose reactive reads should not result in reactive dependencies being taken (that
    is, we want to read reactive values but are not interested in automatically
    reexecuting when those particular values change).
    """
    return reactcore.isolate()


# Import here at the bottom seems to fix a circular dependency problem.
from . import shinysession
