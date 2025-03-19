from pathlib import Path

from starlette.requests import Request

from shiny import App, Inputs, Outputs, Session, render, ui
from shiny.bookmark import set_global_restore_dir_fn, set_global_save_dir_fn

# Setup bookmark directory
BOOKMARK_DIR = Path(__file__).parent / "bookmarks"
BOOKMARK_DIR.mkdir(exist_ok=True)


def bookmark_dir_fn(id: str) -> Path:
    dir_path = BOOKMARK_DIR / id
    return dir_path


def save_dir_fn(id: str) -> Path:
    dir_path = bookmark_dir_fn(id)
    dir_path.mkdir(exist_ok=True)
    return dir_path


restore_dir_fn = bookmark_dir_fn

set_global_save_dir_fn(save_dir_fn)
set_global_restore_dir_fn(restore_dir_fn)


def app_ui(request: Request):
    return ui.page_fluid(
        ui.h2("Server-Side Bookmarking with Multiple Inputs Test"),
        ui.div(
            ui.input_checkbox("option", "Select Option", False),
            ui.output_text("option_info"),
        ),
        ui.div(
            ui.input_text("note", "Add Note", ""),
            ui.output_text("note_info"),
        ),
        ui.div(
            ui.input_slider("slider", "Select a value", min=0, max=100, value=50),
            ui.output_text("slider_info"),
        ),
        ui.div(
            ui.input_select(
                "select",
                "Choose an option",
                choices={
                    "Option A": "Option A",
                    "Option B": "Option B",
                    "Option C": "Option C",
                },
                selected="Option A",
            ),
            ui.output_text("select_info"),
        ),
        ui.div(
            ui.input_radio_buttons(
                "radio",
                "Radio selection",
                choices={
                    "Choice 1": "Choice 1",
                    "Choice 2": "Choice 2",
                    "Choice 3": "Choice 3",
                },
                selected="Choice 1",
            ),
            ui.output_text("radio_info"),
        ),
        ui.div(
            ui.input_numeric("numeric", "Enter a number", value=0),
            ui.output_text("numeric_info"),
        ),
        ui.input_bookmark_button(),
    )


def server(input: Inputs, output: Outputs, session: Session):
    @session.bookmark.on_bookmark
    async def _(state):
        state.values["option_selected"] = input.option()
        state.values["note"] = input.note()
        state.values["slider_value"] = input.slider()
        state.values["select_option"] = input.select()
        state.values["radio_choice"] = input.radio()
        state.values["numeric_value"] = input.numeric()

    @render.text
    def option_info():
        return f"Option selected: {input.option()}"

    @render.text
    def note_info():
        return f"Note: {input.note()}"

    @render.text
    def slider_info():
        return f"Slider: {input.slider()}"

    @render.text
    def select_info():
        return f"Select: {input.select()}"

    @render.text
    def radio_info():
        return f"Radio: {input.radio()}"

    @render.text
    def numeric_info():
        return f"Numeric: {input.numeric()}"


app = App(app_ui, server, bookmark_store="server")
