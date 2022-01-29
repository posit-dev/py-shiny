# To run this app:
#   python3 app.py

# Then point web browser to:
#   http://localhost:8000/

from shiny import *

# For plot rendering
import numpy as np
import matplotlib.pyplot as plt

ui = page_fluid(
    layout_sidebar(
        panel_sidebar(
            h2("Dynamic UI"),
            output_ui("ui"),
            input_action_button("btn", "Trigger insert/remove ui"),
        ),
        panel_main(
            output_text_verbatim("txt"),
            output_plot("plot"),
        ),
    ),
)


def server(session: Session):
    @reactive()
    def r():
        if session.input["n"] is None:
            return
        return session.input["n"] * 2

    @session.output("txt")
    async def _():
        val = r()
        return f"n*2 is {val}, session id is {get_current_session().id}"

    @session.output("plot")
    @render_plot(alt="A histogram")
    def _():
        np.random.seed(19680801)
        x = 100 + 15 * np.random.randn(437)

        fig, ax = plt.subplots()
        ax.hist(x, session.input["n"], density=True)
        return fig

    @session.output("ui")
    @render_ui()
    def _():
        return input_slider("This slider is rendered via @render_ui()", "N", 0, 100, 20)

    @observe()
    def _():
        btn = session.input["btn"]
        if btn % 2 == 1:
            ui_insert(tags.p("Thanks for clicking!", id="thanks"), "body")
        elif btn > 0:
            ui_remove("#thanks")


app = ShinyApp(ui, server)

if __name__ == "__main__":
    app.run()
    # Alternately, to listen on a TCP port:
    # app.run(conn_type = "tcp")
