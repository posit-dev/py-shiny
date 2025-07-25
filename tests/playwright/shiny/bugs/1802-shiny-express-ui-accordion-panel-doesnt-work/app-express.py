import datetime

from shiny import reactive
from shiny.express import input, ui

with ui.accordion(id="my_accordion"):
    with ui.accordion_panel(title="About"):
        "This is a simple Shiny app."

    with ui.accordion_panel(title="Panel 1"):
        "Some initial content for Panel 1."

    with ui.accordion_panel(title="Panel 2", value="panel_2_val"):
        "Some initial content for Panel 2."

ui.input_action_button("update_button", "Update Panel 2")
ui.input_action_button("add_panel_button", "Add New Panel")

panel_counter = reactive.value(3)


@reactive.effect
@reactive.event(input.update_button)
def _():
    new_content = f"Content updated at: {datetime.datetime.now().strftime('%H:%M:%S')}"
    ui.update_accordion_panel(
        "my_accordion", "panel_2_val", new_content, title="Panel 2 (Updated)"
    )


@reactive.effect
@reactive.event(input.add_panel_button)
def _():
    current_count = panel_counter.get()
    panel_counter.set(current_count + 1)
    ui.insert_accordion_panel(
        "my_accordion",
        f"Panel {current_count}",
        f"This is dynamically added panel {current_count}, created at {datetime.datetime.now().strftime('%H:%M:%S')}",
    )
