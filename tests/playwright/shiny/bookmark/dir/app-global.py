import shutil
from pathlib import Path

from starlette.requests import Request

from shiny import App, Inputs, Outputs, Session, reactive, render, ui
from shiny._utils import rand_hex
from shiny.bookmark._global import set_app_bookmark_callbacks


def app_ui(request: Request):
    return ui.page_fluid(
        ui.input_radio_buttons("letter", "Choose a letter", choices=["A", "B", "C"]),
        ui.h3("Has saved:"),
        ui.output_code("called_saved"),
        ui.h3("Has restored:"),
        ui.output_code("called_restored"),
    )


def server(input: Inputs, ouput: Outputs, session: Session):

    @reactive.effect
    @reactive.event(input.letter, ignore_init=True)
    async def _():
        await session.bookmark()

    @session.bookmark.on_bookmarked
    async def _(url: str):
        await session.bookmark.update_query_string(url)

    @render.code
    def called_saved():
        reactive.invalidate_later(1)
        return str(did_save)

    @render.code
    def called_restored():
        reactive.invalidate_later(1)
        return str(did_restore)


did_save = False
did_restore = False


app = App(app_ui, server, bookmark_store="server")


# Note:
# This is a "temp" directory that is only used for testing and is cleaned up on app
# shutdown. This should NOT be standard behavior of a hosting environment. Instead, it
# should have a persistent directory that can be restored over time.
bookmark_dir = Path(__file__).parent / f"bookmarks-{rand_hex(8)}"
bookmark_dir.mkdir(exist_ok=True)


def restore_bookmark_dir(id: str) -> Path:
    global did_restore
    did_restore = True
    return bookmark_dir / id


def save_bookmark_dir(id: str) -> Path:
    global did_save
    did_save = True
    save_dir = bookmark_dir / id
    save_dir.mkdir(parents=True, exist_ok=True)
    return save_dir


# Same exact app as `app-attr.py`, except we're using global functions to set the save and restore directories.
set_app_bookmark_callbacks(
    app,
    get_bookmark_save_dir=save_bookmark_dir,
    get_bookmark_restore_dir=restore_bookmark_dir,
)

app.on_shutdown(lambda: shutil.rmtree(bookmark_dir))
