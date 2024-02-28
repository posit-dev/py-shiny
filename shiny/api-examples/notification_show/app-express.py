from shiny import reactive
from shiny.express import input, ui

ui.input_action_button("show", "Show")
ui.input_action_button("remove", "Remove")

ids: list[str] = []
n: int = 0


@reactive.effect
@reactive.event(input.show)
def _():
    global ids
    global n
    # Save the ID for removal later
    id = ui.notification_show("Message " + str(n), duration=None)
    ids.append(id)
    n += 1


@reactive.effect
@reactive.event(input.remove)
def _():
    global ids
    if ids:
        ui.notification_remove(ids.pop())
