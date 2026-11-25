import json
import os
import shutil
from datetime import date, datetime, timedelta
from pathlib import Path

from starlette.requests import Request

from shiny import App, Inputs, Outputs, Session, module, reactive, render, ui
from shiny._utils import rand_hex
from shiny.module import ResolvedId


@module.ui
def module_slider():
    return ui.input_slider(
        "day",
        "Module date",
        date(2026, 1, 1),
        date(2026, 12, 31),
        date(2026, 2, 1),
        step=timedelta(days=1),
    )


def app_ui(request: Request):
    return ui.page_fluid(
        ui.input_slider(
            "day",
            "Date",
            date(2026, 1, 1),
            date(2026, 12, 31),
            date(2026, 2, 1),
            step=timedelta(days=1),
        ),
        ui.input_slider(
            "days",
            "Date range",
            date(2026, 1, 1),
            date(2026, 12, 31),
            (date(2026, 2, 1), date(2026, 3, 1)),
            step=timedelta(days=1),
        ),
        ui.input_slider(
            "moment",
            "Datetime",
            datetime(2026, 1, 1),
            datetime(2026, 12, 31),
            datetime(2026, 2, 1),
            step=timedelta(seconds=1),
            timezone="+0000",
        ),
        ui.input_slider(
            "moments",
            "Datetime range",
            datetime(2026, 1, 1),
            datetime(2026, 12, 31),
            (datetime(2026, 2, 1), datetime(2026, 3, 1)),
            step=timedelta(seconds=1),
            timezone="+0000",
        ),
        ui.input_slider("number", "Number", 0, 10, 2),
        ui.input_slider("numbers", "Number range", 0, 10, (2, 3)),
        module_slider("m"),
        ui.input_action_button("change", "Change values"),
        ui.input_bookmark_button(),
        ui.output_code("values"),
    )


def server(input: Inputs, output: Outputs, session: Session):
    session.bookmark.exclude.append("change")

    @reactive.effect
    @reactive.event(input.change, ignore_init=True)
    def change_values():
        ui.update_slider("day", value=date(2026, 6, 15))
        ui.update_slider("days", value=(date(2026, 6, 15), date(2026, 9, 20)))
        ui.update_slider("moment", value=datetime(2026, 6, 15, 12, 34, 56))
        ui.update_slider(
            "moments",
            value=(datetime(2026, 6, 15, 12, 34, 56), datetime(2026, 9, 20, 1, 2, 3)),
        )
        ui.update_slider("number", value=7)
        ui.update_slider("numbers", value=(6, 9))
        ui.update_slider(ResolvedId("m-day"), value=date(2026, 6, 16))

    @render.code
    def values():
        return json.dumps(
            dict(
                day=input.day(),
                days=input.days(),
                moment=input.moment(),
                moments=input.moments(),
                number=input.number(),
                numbers=input.numbers(),
                module_day=input[ResolvedId("m-day")](),
            ),
            default=str,
        )


store = (
    "server"
    if os.environ.get("SHINY_SLIDER_BOOKMARK_STORE", "url") == "server"
    else "url"
)
app = App(app_ui, server, bookmark_store=store)
# Test-only bookmark directory, removed when the app shuts down.
bookmark_dir = Path(__file__).parent / f"bookmarks-{rand_hex(8)}"
bookmark_dir.mkdir()
app.on_shutdown(lambda: shutil.rmtree(bookmark_dir))


def save_dir(state_id: str) -> Path:
    path = bookmark_dir / state_id
    path.mkdir()
    return path


app.set_bookmark_save_dir_fn(save_dir)
app.set_bookmark_restore_dir_fn(lambda state_id: bookmark_dir / state_id)
