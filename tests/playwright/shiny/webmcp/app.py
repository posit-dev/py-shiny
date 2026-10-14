import asyncio
from typing import cast

from htmltools import Tag

from shiny import App, Inputs, Outputs, Session, module, reactive, render, ui, webmcp


@module.ui
def controls():
    return ui.input_selectize("choice", "Module choice", ["a", "b", "c"], selected="a")


@module.server
def logic(input: Inputs, output: Outputs, session: Session):
    @webmcp.tool(
        description="Read this module's selection",
        input_schema={"type": "object", "properties": {}},
        read_only=True,
    )
    def selection():
        return {"choice": input.choice()}


run_button = ui.input_action_button("run", "Run")
run_button.attrs["data-webmcp"] = "action"

disabled_link = ui.input_action_link("disabled_link", "Disabled link")
disabled_link.attrs["data-webmcp"] = "action"
disabled_link.attrs["disabled"] = ""

aria_disabled_link = ui.input_action_link("aria_disabled_link", "Aria disabled")
aria_disabled_link.attrs["data-webmcp"] = "action"
aria_disabled_link.attrs["aria-disabled"] = "true"

multi_input = ui.input_text("multi_label", "")
cast(Tag, multi_input.children[1]).attrs["aria-labelledby"] = "first_part second_part"

app_ui = ui.page_fluid(
    ui.tags.span("First", id="first_part"),
    ui.tags.span("Second", id="second_part"),
    multi_input,
    disabled_link,
    aria_disabled_link,
    ui.input_numeric("n", "Quantity", 2, min=0, max=10),
    ui.input_text("name", "Name", "Ada"),
    ui.input_checkbox("enabled", "Enabled", True),
    ui.input_checkbox("remove_left", "Remove left module", False),
    ui.input_checkbox_group("colors", "Colors", ["red", "blue"], selected=["red"]),
    ui.input_radio_buttons("mode", "Mode", ["one", "two"]),
    ui.input_slider("range", "Range", min=0, max=10, value=(2, 8)),
    ui.input_date("day", "Day", value="2026-09-01", min="2026-01-01", max="2026-12-31"),
    ui.input_date_range("period", "Period", start="2026-09-01", end="2026-09-03"),
    ui.tags.fieldset(ui.input_numeric("disabled", "Disabled", 1), disabled=True),
    ui.input_password("password", "Password", "secret"),
    ui.div(
        ui.input_text("private", "Private", "private value"),
        **{"data-webmcp": "exclude"},
    ),
    controls("left"),
    controls("right"),
    run_button,
    ui.input_action_button("delete", "Delete"),
    ui.output_text("result"),
    ui.output_text("factor"),
    ui.output_text("dates"),
    ui.output_ui("dynamic"),
)


def server(input: Inputs, output: Outputs, session: Session):
    logic("left")
    logic("right")
    factor_value = reactive.Value(1)

    @webmcp.tool(
        description="Deliberately slow operation for cancellation and timeout tests",
        input_schema={"type": "object", "properties": {}},
    )
    async def slow_operation():
        await session.send_custom_message("slow-operation", {"state": "started"})
        await asyncio.sleep(0.5)
        factor_value.set(42)
        await session.send_custom_message("slow-operation", {"state": "finished"})
        return {"factor": factor_value()}

    @webmcp.tool(
        description="Read the slow operation's side effect",
        input_schema={"type": "object", "properties": {}},
        read_only=True,
    )
    def read_factor():
        return {"factor": factor_value()}

    @reactive.effect
    @reactive.event(input.remove_left)
    async def remove_left():
        if input.remove_left():
            await session.destroy("left")

    @webmcp.tool(
        description="Change the factor",
        input_schema={
            "type": "object",
            "properties": {"factor": {"type": "integer"}},
            "required": ["factor"],
        },
    )
    async def set_factor(factor: int):
        factor_value.set(factor)
        return {"factor": factor_value()}

    @render.text
    def factor():
        return str(factor_value())

    @render.text
    def dates():
        return f"{input.day()}:{input.period()}"

    @render.text
    def result():
        return f"{input.name()}:{input.n()}:{input.enabled()}:{','.join(input.colors())}:{input.mode()}:{input.range()}:{input.run()}"

    @render.ui
    def dynamic():
        if input.n() > 5:
            return ui.input_select("extra", "Extra", ["x", "y"])

    @reactive.effect
    def update_choices():
        if input.n() == 10:
            ui.update_selectize("left-choice", choices=["a", "d"], selected="d")

    @webmcp.tool(
        description="Multiply quantity without changing it",
        input_schema={
            "type": "object",
            "properties": {"factor": {"type": "number", "minimum": 0}},
            "required": ["factor"],
            "additionalProperties": False,
        },
        read_only=True,
    )
    def multiply(factor: float):
        return {"product": input.n() * factor}


app = App(app_ui, server, webmcp=True)
