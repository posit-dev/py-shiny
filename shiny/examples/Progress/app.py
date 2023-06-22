import asyncio

from shiny import App, Inputs, Outputs, Session, reactive, render, ui

app_ui = ui.page_fluid(
    ui.input_action_button("button", "Compute"),
    ui.output_text("compute"),
)


def server(input: Inputs, output: Outputs, session: Session):
    @output
    @render.text
    @reactive.event(input.button)
    async def compute():
        with ui.Progress(min=1, max=15) as p:
            p.set(message="Calculation in progress", detail="This may take a while...")

            for i in range(1, 15):
                p.set(i, message="Computing")
                await asyncio.sleep(0.1)
                # Normally use time.sleep() instead, but it doesn't yet work in Pyodide.
                # https://github.com/pyodide/pyodide/issues/2354

        return "Done computing!"


app = App(app_ui, server)
