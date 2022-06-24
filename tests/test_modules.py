"""Tests for `Module`."""

import asyncio
from typing import Dict, Union, cast

import pytest

from htmltools import Tag, TagList
from shiny import *
from shiny._connection import MockConnection
from shiny._namespaces import resolve_id
from shiny.session import get_current_session


@module.ui
def mod_inner_ui() -> TagList:
    return TagList(
        ui.input_action_button("button", label="inner"),
        ui.output_text(resolve_id("out")),
    )


@module.ui
def mod_outer_ui() -> TagList:
    return TagList(mod_inner_ui("inner"), ui.output_text("out2"))


def get_id(x: TagList, child_idx: int = 0) -> str:
    return cast(Tag, x[child_idx]).attrs["id"]


def test_module_ui():
    x = mod_inner_ui("inner")
    assert get_id(x, 0) == "inner-button"
    assert get_id(x, 1) == "inner-out"
    y = mod_outer_ui("outer")
    assert get_id(y, 0) == "outer-inner-button"
    assert get_id(y, 1) == "outer-inner-out"
    assert get_id(y, 2) == "outer-out2"


@pytest.mark.asyncio
async def test_session_scoping():

    sessions: Dict[str, Union[Session, None, str]] = {}

    @module.server
    def inner_server(input: Inputs, output: Outputs, session: Session):
        @reactive.Calc
        def out():
            return get_current_session()

        @reactive.Effect
        def _():
            sessions["inner"] = session
            sessions["inner_current"] = get_current_session()
            sessions["inner_calc_current"] = out()
            sessions["inner_id"] = session.ns("foo")
            sessions["inner_ui_id"] = get_id(mod_outer_ui("outer"), 0)

    @module.server
    def outer_server(input: Inputs, output: Outputs, session: Session):
        @reactive.Calc
        def out():
            return get_current_session()

        @reactive.Effect
        def _():
            inner_server("mod_inner")
            sessions["outer"] = session
            sessions["outer_current"] = get_current_session()
            sessions["outer_calc_current"] = out()
            sessions["outer_id"] = session.ns("foo")
            sessions["outer_ui_id"] = get_id(mod_outer_ui("outer"), 0)

    def server(input: Inputs, output: Outputs, session: Session):
        outer_server("mod_outer")

        @reactive.Calc
        def out():
            return get_current_session()

        @reactive.Effect
        def _():
            sessions["top"] = session
            sessions["top_current"] = get_current_session()
            sessions["top_calc_current"] = out()
            sessions["top_id"] = session.ns("foo")
            sessions["top_ui_id"] = get_id(mod_outer_ui("outer"), 0)

    conn = MockConnection()
    sess = App(ui.TagList(), server)._create_session(conn)

    async def mock_client():
        conn.cause_receive('{"method":"init","data":{}}')
        conn.cause_disconnect()

    await asyncio.gather(mock_client(), sess._run())

    assert sessions["inner"] is sessions["inner_current"]
    assert sessions["inner_current"] is sessions["inner_calc_current"]
    assert isinstance(sessions["inner_current"], Session)
    assert sessions["inner_id"] == "mod_outer-mod_inner-foo"
    assert sessions["inner_ui_id"] == "mod_outer-mod_inner-outer-inner-button"

    assert sessions["outer"] is sessions["outer_current"]
    assert sessions["outer_current"] is sessions["outer_calc_current"]
    assert isinstance(sessions["outer_current"], Session)
    assert sessions["outer_id"] == "mod_outer-foo"
    assert sessions["outer_ui_id"] == "mod_outer-outer-inner-button"

    assert sessions["top"] is sessions["top_current"]
    assert sessions["top_current"] is sessions["top_calc_current"]
    assert isinstance(sessions["top_current"], Session)
    assert sessions["top_id"] == "foo"
    assert sessions["top_ui_id"] == "outer-inner-button"
