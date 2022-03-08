"""Tests for `Module`."""

from typing import Callable, Dict, Union

import pytest
from shiny import *
from shiny.reactive import Calc_
from shiny.session import get_current_session
from shiny._connmanager import MockConnection
from shiny._modules import ModuleInputs, ModuleSession
from shiny._utils import run_coro_sync
from htmltools import TagChildArg


def mod_ui(ns: Callable[[str], str]) -> TagChildArg:
    return ui.TagList(
        ui.input_action_button(id=ns("button"), label="module1"),
        ui.output_text_verbatim(id=ns("out")),
    )


# Note: We currently can't test Session; this is just here for future use.
def mod_server(input: Inputs, output: Outputs, session: Session):
    count: reactive.Value[int] = reactive.Value(0)

    @reactive.Effect()
    @event(session.input.button)
    def _():
        count.set(count() + 1)

    @output()
    @render_text()
    def out() -> str:
        return f"Click count is {count()}"


mod = Module(mod_ui, mod_server)


def test_module_ui():
    x = mod.ui("mod1")
    assert x[0].attrs["id"] == "mod1-button"
    assert x[1].attrs["id"] == "mod1-out"


@pytest.mark.asyncio
async def test_inputs_proxy():
    input = Inputs(a=1)
    input_proxy = ModuleInputs("mod1", input)

    with reactive.isolate():
        assert input.a() == 1
        # Different ways of accessing "a" from the input proxy.
        assert input_proxy.a.is_set() is False
        assert input_proxy["a"].is_set() is False
        assert input["mod1-a"].is_set() is False

    input_proxy.a._set(2)

    with reactive.isolate():
        assert input.a() == 1
        assert input_proxy.a() == 2
        assert input_proxy["a"]() == 2
        assert input["mod1-a"]() == 2

    # Nested input proxies
    input_proxy_proxy = ModuleInputs("mod2", input_proxy)
    with reactive.isolate():
        assert input.a() == 1
        assert input_proxy.a() == 2
        # Different ways of accessing "a" from the input proxy.
        assert input_proxy_proxy.a.is_set() is False
        assert input_proxy_proxy["a"].is_set() is False
        assert input_proxy["mod1-a"].is_set() is False

    input_proxy_proxy.a._set(3)

    with reactive.isolate():
        assert input.a() == 1
        assert input_proxy.a() == 2
        assert input_proxy_proxy.a() == 3
        assert input_proxy_proxy["a"]() == 3
        assert input["mod1-mod2-a"]() == 3


def test_current_session():

    sessions: Dict[str, Union[Session, None]] = {}

    def inner(
        input: Inputs, output: Outputs, session: Session, top_calc: Calc_[Session]
    ):
        @reactive.Calc()
        def calc():
            return get_current_session()

        @reactive.Effect()
        def _():
            sessions["inner"] = session
            sessions["inner_current"] = get_current_session()
            sessions["inner_calc"] = calc()
            sessions["inner_top_calc"] = top_calc()

    mod_inner = Module(ui.TagList, inner)

    def outer(
        input: Inputs, output: Outputs, session: Session, top_calc: Calc_[Session]
    ):
        @reactive.Calc()
        def calc():
            return get_current_session()

        @reactive.Effect()
        def _():
            sessions["outer"] = session
            sessions["outer_current"] = get_current_session()
            sessions["outer_calc"] = calc()
            sessions["outer_top_calc"] = top_calc()

        mod_inner.server("mod_inner", top_calc=top_calc)

    mod_outer = Module(ui.TagList, outer)

    def server(input: Inputs, output: Outputs, session: Session):
        @reactive.Calc()
        def calc():
            return get_current_session()

        @reactive.Effect()
        def _():
            sessions["top"] = session
            sessions["top_current"] = get_current_session()
            sessions["top_calc"] = calc()

        mod_outer.server("mod_outer", top_calc=calc)

    App(ui.TagList(), server)._create_session(MockConnection())
    run_coro_sync(reactive.flush())

    assert sessions["inner"] is sessions["inner_current"] and sessions["inner_calc"]
    assert isinstance(sessions["inner"], ModuleSession)
    assert sessions["inner"]._ns == "mod_inner"

    assert sessions["outer"] is sessions["outer_current"] and sessions["outer_calc"]
    assert isinstance(sessions["outer"], ModuleSession)
    assert sessions["outer"]._ns == "mod_outer"

    assert sessions["top"] is sessions["top_current"] and sessions["top_calc"]
    assert sessions["top"] is sessions["inner_top_calc"] and sessions["outer_top_calc"]
    assert isinstance(sessions["top"], Session) and not isinstance(
        sessions["top"], ModuleSession
    )
