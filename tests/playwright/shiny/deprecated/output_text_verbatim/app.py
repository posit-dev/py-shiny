import warnings

from shiny import App, Inputs, Outputs, Session, render, ui
from shiny._deprecated import ShinyDeprecationWarning

# `ui.output_text_verbatim()` is deprecated in favor of `ui.output_code()`. This app
# keeps it covered end to end for as long as it still renders an output container.
warnings.filterwarnings("ignore", category=ShinyDeprecationWarning)

app_ui = ui.page_fluid(
    ui.input_text("caption", "Caption", value="Data summary"),
    ui.output_text_verbatim("verbatim"),
    ui.output_text_verbatim("verbatim_placeholder", placeholder=True),
)


def server(input: Inputs, output: Outputs, session: Session):
    @render.text
    def verbatim():
        return input.caption()

    @render.text
    def verbatim_placeholder():
        return input.caption()


app = App(app_ui, server)
