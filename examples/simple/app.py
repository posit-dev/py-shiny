from shiny import *

app_ui = ui.page_fluid(
    ui.input_slider("n", "N", 0, 100, 20),
    ui.output_text_verbatim("txt", placeholder=True),
)

# A Value which is exists outside of the session.
shared_val = Value(None)


def server(input: Inputs, output: Outputs, session: Session):
    @calculate()
    def r():
        if input.n() is None:
            return
        return input.n() * 2

    @output()
    @render_text()
    async def txt():
        val = r()
        return f"n*2 is {val}, session id is {session.id}"


app = App(app_ui, server)
