from __future__ import annotations

import asyncio

from shiny import App, Inputs, Outputs, Session, reactive, render, ui

app_ui = ui.page_fluid(
    ui.markdown(
        """
        # `session.on_flush` and `session.on_flushed` Reprex

        Verify that `on_flush` and `on_flushed` are called in the correct order, and that they can be cancelled, handle, synchronous functions, and handle asynchronous functions.

        It is not safe to put reactivity inside `session.on_flush()` or `session.on_flushed()` callbacks as the reactive graph is not locked. This app breaks that rule to test the behavior as there is only one user. (If there were multiple users, the reactive graph would not be locked could update while waiting for an async callback.)

        The reprex below will click the button twice (click count is `K`), once after 250ms and another after another 250ms. The expected output is:
        * `a-K-EVENT`
        * `bx-K-first-EVENT`
        * `by-K-first-EVENT`
        * `bx-K-second-EVENT`
        * `by-K-second-EVENT`
        * `c-K-EVENT`


        Even though the `flush` and `flushed` events where mixed when being added, all `flush` events should occur before all `flushed` events.

        Without something to continuously trigger the reactive graph, the `K` value will be `1` less than the click count. To combat this, a reactive event will trigger every 250ms to invoke session `flush` / `flushed` callback.

        ## Automated Reprex:
        """
    ),
    ui.input_action_button("btn", "Click me!"),
    ui.tags.br(),
    ui.tags.span("Counter: "),
    ui.output_text_verbatim("btn_txt", placeholder=True),
    ui.tags.span("All events: "),
    ui.output_text_verbatim("all_txt", placeholder=True),
    ui.tags.span("Flush events: "),
    ui.output_text_verbatim("flush_txt", placeholder=True),
    ui.tags.span("Flushed: "),
    ui.output_text_verbatim("flushed_txt", placeholder=True),
    ui.tags.script(
        """
        $(document).on('shiny:connected', function(event) {
            const n = 250
            document.querySelector("#btn").click();
            setTimeout(function() {
                document.querySelector("#btn").click();
            }, n)
            setTimeout(function() {
                document.querySelector("#btn").click();
            }, 2 * n)
        });
        """
    ),
)


def server(input: Inputs, output: Outputs, session: Session):
    def on_ended_sync(txt: str):
        def _():
            print(txt)

        return _

    def on_ended_async(txt: str):
        async def _():
            await asyncio.sleep(0)
            print(txt)

        return _

    cancel_on_ended_sync = session.on_ended(
        on_ended_sync("session ended - sync - cancel")
    )
    cancel_on_ended_async = session.on_ended(
        on_ended_async("session ended - async - cancel")
    )
    session.on_ended(on_ended_sync("session ended - sync - test1"))
    session.on_ended(on_ended_async("session ended - async - test2"))
    session.on_ended(on_ended_async("session ended - async - test3"))
    session.on_ended(on_ended_sync("session ended - sync - test4"))

    all_vals: reactive.Value[tuple[str, ...]] = reactive.Value(())
    flush_vals: reactive.Value[tuple[str, ...]] = reactive.Value(())
    flushed_vals: reactive.Value[tuple[str, ...]] = reactive.Value(())

    def call_a(
        vals: reactive.Value[tuple[str, ...]],
        suffix: str,
    ):
        def _():
            with reactive.isolate():
                all_vals.set(all_vals.get() + (f"a-{suffix}",))
                vals.set(vals.get() + (f"a-{suffix}",))

        return _

    def call_b(
        vals: reactive.Value[tuple[str, ...]],
        suffix: str,
    ):
        async def _():
            with reactive.isolate():
                all_vals.set(all_vals.get() + (f"bx-{suffix}",))
                vals.set(vals.get() + (f"bx-{suffix}",))
            await asyncio.sleep(0)
            with reactive.isolate():
                all_vals.set(all_vals.get() + (f"by-{suffix}",))
                vals.set(vals.get() + (f"by-{suffix}",))

        return _

    def call_c(
        vals: reactive.Value[tuple[str, ...]],
        suffix: str,
    ):
        def _():
            with reactive.isolate():
                all_vals.set(all_vals.get() + (f"c-{suffix}",))
                vals.set(vals.get() + (f"c-{suffix}",))

        return _

    # Continuously trigger the reactive graph to ensure that the flush / flushed
    # callbacks are called. If this Effect is not called, then the click counter will
    # always be one higher than the flush/flushed values displayed.
    @reactive.effect
    def _():
        reactive.invalidate_later(0.25)

    @reactive.effect
    @reactive.event(input.btn)
    def _():
        btn_count = input.btn()

        def reset():
            all_vals.set(())
            flush_vals.set(())
            flushed_vals.set(())

        session.on_flush(reset, once=True)

        session.on_flushed(call_a(flushed_vals, f"{btn_count}-flushed"), once=True)
        session.on_flushed(
            call_b(flushed_vals, f"{btn_count}-first-flushed"), once=True
        )
        session.on_flush(call_a(flush_vals, f"{btn_count}-flush"), once=True)
        cancel_b_flush = session.on_flush(
            call_b(flush_vals, f"{btn_count}-cancel-flush"), once=True
        )
        session.on_flush(call_b(flush_vals, f"{btn_count}-first-flush"), once=True)
        session.on_flushed(
            call_b(flushed_vals, f"{btn_count}-second-flushed"), once=True
        )
        session.on_flush(call_b(flush_vals, f"{btn_count}-second-flush"), once=True)
        session.on_flushed(call_c(flushed_vals, f"{btn_count}-flushed"), once=True)
        cancel_c_flushed = session.on_flushed(
            call_c(flushed_vals, f"{btn_count}-cancel-flushed"), once=True
        )
        session.on_flush(call_c(flush_vals, f"{btn_count}-flush"), once=True)

        cancel_b_flush()
        cancel_c_flushed()
        cancel_on_ended_sync()
        cancel_on_ended_async()

    @render.text
    def btn_txt():
        return str(input.btn())

    @render.text
    def all_txt():
        return str(all_vals.get())

    @render.text
    def flush_txt():
        return str(flush_vals.get())

    @render.text
    def flushed_txt():
        return str(flushed_vals.get())


app = App(app_ui, server)
