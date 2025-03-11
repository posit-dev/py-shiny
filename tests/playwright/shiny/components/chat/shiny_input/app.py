from shiny import reactive
from shiny.express import input, ui

ui.page_opts(title="Testing input bindings in Chat", gap="3rem")

welcome = ui.TagList(
    "**Hello! Here are a couple inputs:**",
    ui.div(
        ui.input_select("select", "", choices=["a", "b", "c"], width="fit-content"),
        ui.input_switch("toggle", "Toggle", width="fit-content"),
        ui.input_action_button("insert_input", "Insert input"),
        class_="d-flex gap-5",
    ),
    ui.div(
        ui.head_content(ui.tags.style("#chat { color: #29465B; }")),
    ),
)

chat = ui.Chat(
    id="chat",
    messages=[welcome],
)
chat.ui(class_="mb-5")


@reactive.effect
async def _():
    await chat.append_message(f"Now selected: {input.select()} and {input.toggle()}")


@reactive.effect
@reactive.event(input.insert_input)
async def _():
    await chat.append_message_stream(
        [
            "Here's ",
            "another ",
            "input: ",
            ui.input_numeric("numeric", "", value=0),
        ]
    )
    ui.update_action_button("insert_input", disabled=True)


@reactive.effect
@reactive.event(input.numeric, ignore_init=True)
async def _():
    await chat.append_message(f"Numeric value: {input.numeric()}")
