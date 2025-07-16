import asyncio
import hashlib
import time

from shiny import App, Inputs, Outputs, Session, reactive, render, ui


def calc(value: str) -> str:
    # Simluate this taking a long time
    time.sleep(1)
    m = hashlib.sha256()
    m.update(value.encode("utf-8"))
    return m.digest().hex()


app_ui = ui.page_fluid(
    ui.input_text_area(
        "value", "Value to sha256sum", value="The quick brown fox", rows=5, width="100%"
    ),
    ui.p(ui.input_action_button("go", "Calculate"), class_="mb-3"),
    ui.output_text_verbatim("hash_output"),
)


def server(input: Inputs, output: Outputs, session: Session):
    @render.text()
    @reactive.event(input.go)
    async def hash_output():
        content = await hash_result()
        return content

    @reactive.calc()
    async def hash_result() -> str:
        with ui.Progress() as p:
            p.set(message="Calculating...")

            value = input.value()
            return await asyncio.get_running_loop().run_in_executor(None, calc, value)


app = App(app_ui, server)
