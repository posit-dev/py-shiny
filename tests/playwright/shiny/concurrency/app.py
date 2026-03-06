import asyncio

from shiny import App, Inputs, Outputs, Session, reactive, render, ui

app_ui = ui.page_fluid(
    ui.input_action_button("btn", "Increment"),
    ui.output_text_verbatim("current_value"),
    ui.output_text_verbatim("effect_log"),
)


def server(input: Inputs, output: Outputs, session: Session) -> None:
    log: list[int] = []

    @render.text
    def current_value() -> str:
        return str(int(input.btn()))

    @render.text
    @reactive.event(input.btn)
    async def effect_log() -> str:
        counter_val = int(input.btn())
        await asyncio.sleep(0.3)
        log.append(counter_val)
        return str(log)


app = App(app_ui, server)
