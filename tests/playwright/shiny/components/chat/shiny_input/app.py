from shiny import reactive
from shiny.express import input, ui

ui.page_opts(
    title="Hello input bindings in Chat",
    fillable=True,
    fillable_mobile=True,
)

welcome = f"""
**Hello! Here are some inputs:**

{ui.input_select("select", "", choices=["a", "b", "c"])}
{ui.input_slider("slider", "", min=0, max=100, value=50)}
"""

chat = ui.Chat(
    id="chat",
    messages=[welcome],
)
chat.ui()


@reactive.effect
async def _():
    await chat.append_message(f"Now selected: {input.select()} and {input.slider()}")
