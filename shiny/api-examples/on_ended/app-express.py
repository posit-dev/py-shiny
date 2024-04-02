from datetime import datetime

from shiny import reactive
from shiny.express import input, session, ui

ui.input_action_button("close", "Close the session")


def log():
    print("Session ended at: " + datetime.now().strftime("%H:%M:%S"))


_ = session.on_ended(log)


@reactive.effect
@reactive.event(input.close)
async def _():
    await session.close()
