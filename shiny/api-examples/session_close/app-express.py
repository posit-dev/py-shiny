from datetime import datetime

from shiny import reactive
from shiny.express import input, session, ui

ui.input_action_button("close", "Close the session")
ui.p(
    """If this example is running on the browser (i.e., via shinylive),
    closing the session will log a message to the JavaScript console
    (open the browser's developer tools to see it).
    """
)


def log():
    print("Session ended at: " + datetime.now().strftime("%H:%M:%S"))


_ = session.on_ended(log)


@reactive.effect
@reactive.event(input.close)
async def _():
    await session.close()
