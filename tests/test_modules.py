"""Tests for `Module`."""

import pytest

from shiny import *
from shiny.modules import *
from shiny._utils import Callable
from shiny.reactive import isolate
from htmltools import TagChildArg


def mod_ui(ns: Callable[[str], str]) -> TagChildArg:
    return ui.TagList(
        ui.input_action_button(id=ns("button"), label="module1"),
        ui.output_text_verbatim(id=ns("out")),
    )


# Note: We currently can't test Session; this is just here for future use.
def mod_server(input: ModuleInputs, output: ModuleOutputs, session: ModuleSession):
    count: Value[int] = Value(0)

    @effect()
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

    with isolate():
        assert input.a() == 1
        # Different ways of accessing "a" from the input proxy.
        assert input_proxy.a() is None
        assert input_proxy["a"]() is None
        assert input["mod1-a"]() is None

    input_proxy.a._set(2)

    with isolate():
        assert input.a() == 1
        assert input_proxy.a() == 2
        assert input_proxy["a"]() == 2
        assert input["mod1-a"]() == 2

    # Nested input proxies
    input_proxy_proxy = ModuleInputs("mod2", input_proxy)
    with isolate():
        assert input.a() == 1
        assert input_proxy.a() == 2
        # Different ways of accessing "a" from the input proxy.
        assert input_proxy_proxy.a() is None
        assert input_proxy_proxy["a"]() is None
        assert input["mod1-mod2-a"]() is None

    input_proxy_proxy.a._set(3)

    with isolate():
        assert input.a() == 1
        assert input_proxy.a() == 2
        assert input_proxy_proxy.a() == 3
        assert input_proxy_proxy["a"]() == 3
        assert input["mod1-mod2-a"]() == 3
