import asyncio

from shiny import App, Inputs, Outputs, Session, reactive, render, ui

app_ui = ui.page_fluid(
    ui.input_action_button("block", "Run slow async effect"),
    ui.output_text("ticks"),
)


def server(input: Inputs, output: Outputs, session: Session) -> None:
    n = reactive.value(0)

    @reactive.effect
    def _tick():
        reactive.invalidate_later(0.1)
        with reactive.isolate():
            n.set(n() + 1)

    @reactive.effect
    @reactive.event(input.block)
    async def _slow():
        await asyncio.sleep(3)

    @render.text
    def ticks():
        return str(n())


app = App(app_ui, server)
