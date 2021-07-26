import react

class Dependents:

    def __init__(self) -> None:
        self._dependents = {}

    def register(self) -> None:
        ctx = react.get_current_context()
        if (ctx.id not in self._dependents):
            self._dependents[ctx.id] = ctx

        ctx.on_invalidate(lambda: self._dependents.pop(ctx.id))

    def invalidate(self) -> None:
        for id in sorted(self._dependents.keys()):
            ctx = self._dependents[id]
            ctx.invalidate()



class ReactiveVal:
    def __init__(self, value) -> None:
        self._value = value
        self._dependents = Dependents()

    def get(self):
        self._dependents.register()
        return self._value
    
    def set(self, value) -> None:
        if (self._value is value):
            return False
        
        self._value = value
        self._dependents.invalidate()
        return True


class Observable:
    def __init__(self, func: callable) -> None:
        # TODO: Check number of args for func
        self._func = func
        self._dependents = Dependents()
        self._invalidated = True
        self._running = False
        self._most_recent_ctx_id = ""
        self._ctx = None

    def get_value(self):
        self._dependents.register()

        if (self._invalidated or self._running):
            self.update_value()
        
        return self._value


    def update_value(self) -> None:
        self._ctx = react.Context()
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
        # TODO: Wrap in try-catch
        self._value = self._func()


def reactive(func: callable) -> callable:
    o = Observable(func)
    return lambda: o.get_value()





class Observer:
    def __init__(self, func: callable) -> None:
        # TODO: Check number of args for func
        self._func = func
        self._invalidate_callbacks = []
        self._destroyed = False
        self._ctx = None
        self._prev_ctx_id = ""

        # Defer the first running of this until flushReact is called
        self._create_context().invalidate()

    def _create_context(self) -> react.Context:
        ctx = react.Context()
        self._prev_ctx_id = ctx.id

        # Store the context explicitly in Observer object
        # TODO: More explanation here
        self._ctx = ctx

        def _on_invalidate_cb() -> None:
            # Context is invalidated, so we don't need to store a reference to it
            # anymore.
            self._ctx = None

            for cb in self._invalidate_callbacks:
                cb()
            
            # TODO: Wrap this stuff up in a continue callback, depending on if suspended?
            ctx.add_pending_flush()


        def _on_flush_cb() -> None:
            if not self._destroyed:
                self.run()
        
        ctx.on_invalidate(_on_invalidate_cb)
        ctx.on_flush(_on_flush_cb)

        return ctx

    def run(self) -> None:
        ctx = react.Context()
        ctx.run(self._func)

    def on_invalidate(self, callback: callable) -> None:
        self._invalidate_callbacks.append(callback)

    def destroy(self) -> None:
        self._destroyed = True

        if (self._ctx is not None):
            self._ctx.invalidate()



def observe(func: callable) -> Observer:
    o = Observer(func)
    return o




if (__name__ == '__main__'):
    x = ReactiveVal(1)
    x.set(2)

    # Reactive expression
    r = reactive(lambda: x.get() + 10)

    x.set(3)

    observe(lambda: print(r() + 100))

    x.set(4)

    # Should print '114'
    react.flush_react()
