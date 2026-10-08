"""A `reactive.calc` that calls itself recursively, driven by a shared mutable
local, re-created fresh on every render. One output exercises the sync
`Calc_` path, the other the async `CalcAsync_` path -- both share the same
`get_value`/`update_value`/`_run_func` machinery in `Calc_`, so both need
covering.

Regression app for the `Calc_` recursion fix: before the fix, every call
returned the *first* value ever computed by the recursion (the base case),
because `get_value()` read a shared `self._value[0]`/`self._error[0]` cache
that a reentrant recursive call clobbered before the outer call could read it.

`fib` is defined inside the output function, rather than at module/server
scope, so each render gets its own fresh `Calc_` (never invalidated/re-invoked
across renders) -- isolating the recursion bug from the unrelated fact that a
`reactive.calc` with no tracked reactive dependency never recomputes.

This does *not* cover concurrent/interleaved calls to the same `Calc_` (for
example two `asyncio.gather()`'d calls racing a shared no-arg async calc) --
that remains unsupported, since the calls would still share one `_running`
flag and one mutable external mapping an arg would otherwise have been.
"""

from shiny import App, Inputs, Outputs, Session, reactive, render, ui

app_ui = ui.page_fixed(
    ui.input_numeric("n", "Number", value=5),
    ui.output_text("result"),
    ui.output_text("result_async"),
)


def server(input: Inputs, output: Outputs, session: Session):
    @render.text
    def result():
        i = input.n()

        @reactive.calc
        def fib() -> int:
            nonlocal i
            if i < 2:
                return 1
            i -= 1
            return 1 + fib()

        return str(fib())

    @render.text
    async def result_async():
        i = input.n()

        @reactive.calc
        async def fib() -> int:
            nonlocal i
            if i < 2:
                return 1
            i -= 1
            return 1 + await fib()

        return str(await fib())


app = App(app_ui, server)
