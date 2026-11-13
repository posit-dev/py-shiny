import asyncio
from typing import AsyncIterable

from shiny import App, Inputs, Outputs, Session, reactive, render, ui

app_ui = ui.page_fluid(
    ui.download_button("dl", "Download"),
    ui.input_action_button("release", "Finish download"),
    ui.output_text("status"),
)


def server(input: Inputs, output: Outputs, session: Session) -> None:
    state = reactive.value("idle")
    release = asyncio.Event()

    @reactive.effect
    @reactive.event(input.release)
    def _():
        release.set()

    @render.download_button(filename="streamed.txt")
    async def dl() -> AsyncIterable[str]:
        state.set("streaming")
        yield "first,"
        # The stream stays open until the session handles the button click.
        await release.wait()
        state.set("done")
        yield "second"

    @render.text
    def status():
        return state()


app = App(app_ui, server)
