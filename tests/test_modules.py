"""Tests for `Module`."""

from typing import Dict, Union, cast

import pytest
from shiny import *
from shiny.session import get_current_session
from shiny._connection import MockConnection
from shiny._modules import ModuleInputs, ModuleSession
from shiny._utils import run_coro_sync
from htmltools import TagChildArg


def mod_ui() -> TagChildArg:
    return ui.TagList(
        ui.input_action_button(id="button", label="module1"),
        ui.output_text_verbatim(id="out"),
    )


# Note: We currently can't test Session; this is just here for future use.
def mod_server(input: Inputs, output: Outputs, session: Session):
    count: reactive.Value[int] = reactive.Value(0)

    @reactive.Effect
    @event(session.input.button)
    def _():
        count.set(count() + 1)

    @output
    @render.text
    def out() -> str:
        return f"Click count is {count()}"


mod = Module(mod_ui, mod_server)


def test_module_ui():
    x = cast(ui.TagList, mod.ui("mod1"))
    assert cast(ui.Tag, x[0]).attrs["id"] == "mod1_button"
    assert cast(ui.Tag, x[1]).attrs["id"] == "mod1_out"


@pytest.mark.asyncio
async def test_inputs_proxy():
    input = Inputs(a=1)
    input_proxy = ModuleInputs("mod1", input)

    with reactive.isolate():
        assert input.a() == 1
        # Different ways of accessing "a" from the input proxy.
        assert input_proxy.a.is_set() is False
        assert input_proxy["a"].is_set() is False
        assert input["mod1_a"].is_set() is False

    input_proxy.a._set(2)

    with reactive.isolate():
        assert input.a() == 1
        assert input_proxy.a() == 2
        assert input_proxy["a"]() == 2
        assert input["mod1_a"]() == 2

    # Nested input proxies
    input_proxy_proxy = ModuleInputs("mod2", input_proxy)
    with reactive.isolate():
        assert input.a() == 1
        assert input_proxy.a() == 2
        # Different ways of accessing "a" from the input proxy.
        assert input_proxy_proxy.a.is_set() is False
        assert input_proxy_proxy["a"].is_set() is False
        assert input_proxy["mod1_a"].is_set() is False

    input_proxy_proxy.a._set(3)

    with reactive.isolate():
        assert input.a() == 1
        assert input_proxy.a() == 2
        assert input_proxy_proxy.a() == 3
        assert input_proxy_proxy["a"]() == 3
        assert input["mod1_mod2_a"]() == 3


def test_current_session():

    sessions: Dict[str, Union[Session, None]] = {}

    def inner(input: Inputs, output: Outputs, session: Session):
        @reactive.Calc
        def out():
            return get_current_session()

        @reactive.Effect
        def _():
            sessions["inner"] = session
            sessions["inner_current"] = get_current_session()
            sessions["inner_calc_current"] = out()

    mod_inner = Module(ui.TagList, inner)

    def outer(input: Inputs, output: Outputs, session: Session):
        @reactive.Calc
        def out():
            return get_current_session()

        @reactive.Effect
        def _():
            mod_inner.server("mod_inner")
            sessions["outer"] = session
            sessions["outer_current"] = get_current_session()
            sessions["outer_calc_current"] = out()

    mod_outer = Module(ui.TagList, outer)

    def server(input: Inputs, output: Outputs, session: Session):
        mod_outer.server("mod_outer")

        @reactive.Calc
        def out():
            return get_current_session()

        @reactive.Effect
        def _():
            sessions["top"] = session
            sessions["top_current"] = get_current_session()
            sessions["top_calc_current"] = out()

    App(ui.TagList(), server)._create_session(MockConnection())
    run_coro_sync(reactive.flush())

    assert sessions["inner"] is sessions["inner_current"]
    assert sessions["inner_current"] is sessions["inner_calc_current"]
    assert isinstance(sessions["inner_current"], ModuleSession)
    assert sessions["inner_current"]._ns == "mod_outer_mod_inner"

    assert sessions["outer"] is sessions["outer_current"]
    assert sessions["outer_current"] is sessions["outer_calc_current"]
    assert isinstance(sessions["outer_current"], ModuleSession)
    assert sessions["outer_current"]._ns == "mod_outer"

    assert sessions["top"] is sessions["top_current"]
    assert sessions["top_current"] is sessions["top_calc_current"]
    assert isinstance(sessions["top_current"], Session)
    assert not isinstance(sessions["top_current"], ModuleSession)
