from typing import Optional, Any, Callable
from reactcore import Context, Dependents
import reactcore


class ReactiveVal:
    def __init__(self, value: Any) -> None:
        self._value: Any = value
        self._dependents: Dependents = Dependents()

    def __call__(self, *args: Optional[Any]) -> Any:
        if args:
            if len(args) > 1:
                raise TypeError("ReactiveVal can only be called with one argument")
            self.set(args[0])
        else:
            return self.get()

    def get(self) -> Any:
        self._dependents.register()
        return self._value

    def set(self, value: Any) -> bool:
        if (self._value is value):
            return False

        self._value = value
        self._dependents.invalidate()
        return True



class ReactiveValues:
    def __init__(self, **kwargs: Any) -> None:
        self._map: dict[str, Any] = {}
        for key, value in kwargs.items():
            self._map[key] = ReactiveVal(value)

    def __setitem__(self, key: str, value: Any) -> None:
        if (key in self._map):
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



class Reactive:
    def __init__(self, func: Callable[[], Any]) -> None:
        self._func: Callable[[], Any] = func
        self._dependents: Dependents = Dependents()
        self._invalidated: bool = True
        self._running: bool = False
        self._most_recent_ctx_id: int = -1
        self._ctx: Optional[Context] = None

        self._value: Any = None
        self._error: bool = False

    def __call__(self) -> Any:
        return self.get_value()

    def get_value(self) -> Any:
        self._dependents.register()

        if (self._invalidated or self._running):
            self.update_value()

        if (self._error):
            raise self._value

        return self._value

    def update_value(self) -> None:
        self._ctx = Context()
        self._most_recent_ctx_id = self._ctx.id

        self._ctx.on_invalidate(self._on_invalidate_cb)

        self._invalidated = False

        was_running = self._running
        self._running = True

        self._ctx.run(self._run_func)

        # TODO: This should be guaranteed to run; maybe use try?
        self._running = was_running

    def _on_invalidate_cb(self) -> None:
        self._invalidated = True
        self._value = None  # Allow old value to be GC'd
        self._dependents.invalidate()
        self._ctx = None    # Allow context to be GC'd

    def _run_func(self) -> None:
        self._error = False
        try:
            self._value = self._func()
        except Exception as err:
            self._error = True
            self._value = err



class Observer:
    def __init__(self, func: Callable[[], None]) -> None:
        # TODO: Check number of args for func
        self._func: Callable[[], None] = func
        self._invalidate_callbacks: list[Callable[[], None]] = []
        self._destroyed: bool = False
        self._ctx: Optional[Context] = None

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
            ctx.add_pending_flush()

        def on_flush_cb() -> None:
            if not self._destroyed:
                self.run()

        ctx.on_invalidate(on_invalidate_cb)
        ctx.on_flush(on_flush_cb)

        return ctx

    def run(self) -> None:
        ctx = self._create_context()
        ctx.run(self._func)

    def on_invalidate(self, callback: Callable[[], None]) -> None:
        self._invalidate_callbacks.append(callback)

    def destroy(self) -> None:
        self._destroyed = True

        if (self._ctx is not None):
            self._ctx.invalidate()



if (__name__ == '__main__'):
    x = ReactiveVal(1)
    x(2)

    r_count = 0
    @Reactive
    def r():
        print("Executing user reactive function")
        global r_count
        r_count += 1
        return x() + r_count*10

    x(3)

    o_count = 0
    @Observer
    def xx():
        print("Executing user observer function")
        global o_count
        o_count += 1
        print(r() + o_count*100)

    x(4)

    # Should print '114'
    reactcore.flush()

    # Should do nothing
    reactcore.flush()

    x(5)
    # Should print '225'
    reactcore.flush()

    rv = ReactiveValues(a=1, b=2, x=3)
