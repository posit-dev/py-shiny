from typing import Callable, Optional

class Context:
    """A reactive context"""

    def __init__(self) -> None:
        self.id: int = _reactive_environment.next_id()
        self._invalidated: bool = False
        self._invalidate_callbacks: list[Callable[[], None]] = []
        self._flush_callbacks: list[Callable[[], None]] = []

    def run(self, func: Callable[[], None]) -> None:
        """Run the provided function in this context"""
        env = _reactive_environment
        env.run_with(self, func)

    def invalidate(self) -> None:
        """Invalidate this context. It will immediately call the callbacks
        that have been registered with onInvalidate()."""

        if (self._invalidated):
            return


        self._invalidated = True

        for cb in self._invalidate_callbacks:
            cb()

        self._invalidate_callbacks.clear()

    def on_invalidate(self, func: Callable[[], None]) -> None:
        """Register a function to be called when this context is invalidated"""
        if (self._invalidated):
            func()
        else:
            self._invalidate_callbacks.append(func)

    def add_pending_flush(self) -> None:
        """Tell the reactive environment that this context should be flushed the
        next time flushReact() called."""
        _reactive_environment.add_pending_flush(self)

    def on_flush(self, func: Callable[[], None]) -> None:
        """Register a function to be called when this context is flushed."""
        self._flush_callbacks.append(func)

    def execute_flush_callbacks(self) -> None:
        """Execute all flush callbacks"""
        for cb in self._flush_callbacks:
            try:
                cb()
            finally:
                pass

        self._flush_callbacks.clear()


class Dependents:
    def __init__(self) -> None:
        self._dependents: dict[int, Context] = {}

    def register(self) -> None:
        ctx: Context = get_current_context()
        if (ctx.id not in self._dependents):
            self._dependents[ctx.id] = ctx

        def on_invalidate_cb() -> None:
            if (ctx.id in self._dependents):
                del self._dependents[ctx.id]

        ctx.on_invalidate(on_invalidate_cb)

    def invalidate(self) -> None:
        # TODO: Check sort order
        for id in sorted(self._dependents.keys()):
            ctx = self._dependents[id]
            ctx.invalidate()


class ReactiveEnvironment:
    """The reactive environment"""

    def __init__(self) -> None:
        self._context_stack: list[Context] = []
        self._next_id: int = 0
        self._pending_flush: list[Context] = []

    def next_id(self) -> int:
        """Return the next available id"""
        id = self._next_id
        self._next_id += 1
        return id

    def current_context(self) -> Context:
        """Return the current Context object"""
        if not self._context_stack:
            raise Exception("No current context")

        # The Context at the top of the stack.
        return self._context_stack[-1]

    def run_with(self, ctx: Context, contextFunc: Callable[[], None]) -> None:
        self._context_stack.append(ctx)
        try:
            contextFunc()
        finally:
            self._context_stack.pop()

    def flush(self) -> None:
        """Flush all pending operations"""
        for ctx in self._pending_flush:
            try:
                ctx.execute_flush_callbacks()
            finally:
                pass

        self._pending_flush.clear()

    def add_pending_flush(self, ctx: Context) -> None:
        self._pending_flush.append(ctx)



_reactive_environment = ReactiveEnvironment()

def get_current_context() -> Context:
    return _reactive_environment.current_context()


def flush() -> None:
    _reactive_environment.flush()
