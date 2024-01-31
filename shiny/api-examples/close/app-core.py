from datetime import datetime

from shiny import App, Inputs, Outputs, Session, reactive, ui

app_ui = ui.page_fluid(
    ui.input_action_button("close", "Close the session"),
    ui.p(
        """If this example is running on the browser (i.e., via shinylive),
        closing the session will log a message to the JavaScript console
        (open the browser's developer tools to see it).
        """
    ),
)


def server(input: Inputs, output: Outputs, session: Session):
    def log():
        print("Session ended at: " + datetime.now().strftime("%H:%M:%S"))

    session.on_ended(log)

    @reactive.Effect
    @reactive.event(input.close)
    async def _():
        await session.close()


app = App(app_ui, server)
