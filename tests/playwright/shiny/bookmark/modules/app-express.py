import os
from typing import Literal

from shiny import Inputs, Outputs, Session, reactive, render
from shiny.bookmark import BookmarkState
from shiny.bookmark._restore_state import RestoreState
from shiny.express import app_opts, module, session, ui

SHINY_BOOKMARK_STORE: Literal["url", "server"] = os.getenv(
    "SHINY_BOOKMARK_STORE", "url"
)  # pyright: ignore[reportAssignmentType]
if SHINY_BOOKMARK_STORE not in ["url", "server"]:
    raise ValueError("SHINY_BOOKMARK_STORE must be either 'url' or 'server'")

app_opts(bookmark_store=SHINY_BOOKMARK_STORE)


@session.bookmark.on_bookmarked
async def _(url: str):
    await session.bookmark.update_query_string(url)


@render.code
def bookmark_store():
    return f"{session.bookmark.store}"


@module
def ex_mod(input: Inputs, output: Outputs, session: Session, recurse: int = 3):

    ui.h3(f"Module {recurse}")
    with ui.layout_column_wrap(width="200px"):
        ui.TagList(
            ui.input_radio_buttons(
                "btn1", "Button Input", choices=["a", "b", "c"], selected="a"
            ),
            ui.input_radio_buttons(
                "btn2",
                "Button Value",
                choices=["a", "b", "c"],
                selected="a",
            ),
        )

        @render.ui
        def ui_html():
            return ui.TagList(
                ui.input_radio_buttons(
                    "dyn1", "Dynamic Input", choices=["a", "b", "c"], selected="a"
                ),
                ui.input_radio_buttons(
                    "dyn2", "Dynamic Value", choices=["a", "b", "c"], selected="a"
                ),
            )

        @render.code
        def value():
            value_arr = [input.btn1(), input.btn2(), input.dyn1(), input.dyn2()]
            return f"{value_arr}"

    ui.hr()

    @reactive.effect
    @reactive.event(input.btn1, input.btn2, input.dyn1, input.dyn2, ignore_init=True)
    async def _():
        # print("app-Bookmarking!")
        await session.bookmark()

    session.bookmark.exclude.append("btn2")
    session.bookmark.exclude.append("dyn2")

    @session.bookmark.on_bookmark
    def _(state: BookmarkState) -> None:
        state.values["btn2"] = input.btn2()
        state.values["dyn2"] = input.dyn2()

    @session.bookmark.on_restore
    def _(restore_state: RestoreState) -> None:
        # print("app-Restore state:", restore_state.values)

        if "btn2" in restore_state.values:

            ui.update_radio_buttons("btn2", selected=restore_state.values["btn2"])

        if "dyn2" in restore_state.values:

            ui.update_radio_buttons("dyn2", selected=restore_state.values["dyn2"])


"Click Button to update bookmark"

k = 4
for i in reversed(range(k)):
    ex_mod(f"mod{i}", i)
