import tempfile
import time
import uuid
from pathlib import Path

from shiny import App, Inputs, Outputs, Session, module, reactive, render, ui


@module.ui
def button_ui():
    return ui.TagList(
        ui.input_task_button("btn", label="Go"),
        ui.output_text("text_counter"),
        ui.output_text("release_file"),
    )


@module.server
def button_server(input: Inputs, output: Outputs, session: Session):
    counter = reactive.value(0)
    # The button stays "busy" only while the click effect runs. Instead of a
    # hard-coded sleep (which races against how quickly the test can observe
    # the busy state), hold the effect until the test creates this file. The
    # path is unique per session so parallel test runs cannot interfere.
    release_path = Path(tempfile.gettempdir()) / f"task-button2-{uuid.uuid4().hex}"

    @render.text
    def release_file():
        return str(release_path)

    @render.text
    def text_counter():
        return f"Button clicked {counter()} times"

    @reactive.effect
    @reactive.event(input.btn)
    def increment_counter():
        # Deadline so a broken test fails instead of wedging the app forever
        deadline = time.time() + 30
        while not release_path.exists() and time.time() < deadline:
            time.sleep(0.05)
        release_path.unlink(missing_ok=True)
        counter.set(counter() + 1)


app_ui = ui.page_fluid(button_ui("mod1"))


def server(input: Inputs, output: Outputs, session: Session):
    button_server("mod1")


app = App(app_ui, server)
