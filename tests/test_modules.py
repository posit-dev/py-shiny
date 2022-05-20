"""Tests for `Module`."""

from typing import Dict, Union, cast

from shiny import *
from shiny.session import get_current_session
from shiny._connection import MockConnection
from shiny._namespaces import namespaced_id
from shiny._utils import run_coro_sync
from htmltools import TagList, Tag


@module_ui
def mod_inner() -> TagList:
    return TagList(
        ui.input_action_button("button", label="inner"),
        ui.output_text(namespaced_id("out")),
    )


@module_ui
def mod_outer() -> TagList:
    return TagList(mod_inner("inner"), ui.output_text("out2"))


def get_id(x: TagList, child_idx: int = 0) -> str:
    return cast(Tag, x[child_idx]).attrs["id"]


def test_module_ui():
    x = mod_inner("inner")
    assert get_id(x, 0) == "inner_button"
    assert get_id(x, 1) == "inner_out"
    y = mod_outer("outer")
    assert get_id(y, 0) == "outer_inner_button"
    assert get_id(y, 1) == "outer_inner_out"
    assert get_id(y, 2) == "outer_out2"


def test_session_scoping():

    sessions: Dict[str, Union[Session, None, str]] = {}

    @module_server
    def inner(input: Inputs, output: Outputs, session: Session):
        @reactive.Calc
        def out():
            return get_current_session()

        @reactive.Effect
        def _():
            sessions["inner"] = session
            sessions["inner_current"] = get_current_session()
            sessions["inner_calc_current"] = out()
            sessions["inner_id"] = session.ns("foo")
            sessions["inner_ui_id"] = get_id(mod_outer("outer"), 0)

    @module_server
    def outer(input: Inputs, output: Outputs, session: Session):
        @reactive.Calc
        def out():
            return get_current_session()

        @reactive.Effect
        def _():
            inner("mod_inner")
            sessions["outer"] = session
            sessions["outer_current"] = get_current_session()
            sessions["outer_calc_current"] = out()
            sessions["outer_id"] = session.ns("foo")
            sessions["outer_ui_id"] = get_id(mod_outer("outer"), 0)

    def server(input: Inputs, output: Outputs, session: Session):
        outer("mod_outer")

        @reactive.Calc
        def out():
            return get_current_session()

        @reactive.Effect
        def _():
            sessions["top"] = session
            sessions["top_current"] = get_current_session()
            sessions["top_calc_current"] = out()
            sessions["top_id"] = session.ns("foo")
            sessions["top_ui_id"] = get_id(mod_outer("outer"), 0)

    App(ui.TagList(), server)._create_session(MockConnection())
    run_coro_sync(reactive.flush())

    assert sessions["inner"] is sessions["inner_current"]
    assert sessions["inner_current"] is sessions["inner_calc_current"]
    assert isinstance(sessions["inner_current"], Session)
    assert sessions["inner_id"] == "mod_outer_mod_inner_foo"
    assert sessions["inner_ui_id"] == "outer_inner_button"

    assert sessions["outer"] is sessions["outer_current"]
    assert sessions["outer_current"] is sessions["outer_calc_current"]
    assert isinstance(sessions["outer_current"], Session)
    assert sessions["outer_id"] == "mod_outer_foo"
    assert sessions["outer_ui_id"] == "outer_inner_button"

    assert sessions["top"] is sessions["top_current"]
    assert sessions["top_current"] is sessions["top_calc_current"]
    assert isinstance(sessions["top_current"], Session)
    assert sessions["top_id"] == "foo"
    assert sessions["top_ui_id"] == "outer_inner_button"
