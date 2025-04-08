from shiny import reactive
from shiny.express import input, render, ui

md_stream = ui.MarkdownStream("stream")
md_stream.ui(
    content=ui.TagList(
        "**Hello! Here are a couple inputs:**",
        ui.div(
            ui.input_select("select", "", choices=["a", "b", "c"], width="fit-content"),
            ui.input_switch("toggle", "Toggle", width="fit-content"),
            ui.input_action_button("insert_input", "Insert another input"),
            class_="d-flex gap-5",
        ),
        ui.div(
            ui.head_content(ui.tags.style("#chat { color: #29465B; }")),
        ),
    )
)


@reactive.effect
@reactive.event(input.insert_input)
async def _():
    await md_stream.stream(
        ["Here's a dynamically added input: ", ui.input_text("text", "")],
        clear=False,
    )


@render.code
def input_vals():
    return f"Selected: {input.select()} Toggled: {input.toggle()}"


@render.code
def dynamic_input_output():
    return f"Dynamic input value: '{input.text()}'"
