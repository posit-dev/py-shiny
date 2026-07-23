# pyright:basic
import time
from typing import Callable, Literal

from shiny import App, Inputs, Outputs, Session, module, reactive, render, ui

SpinnerType = Literal["ring", "bars", "dots", "pulse"]


# -- Reusable card module --
@module.ui
def card_ui(spinner_type: SpinnerType, spinner_color: str, spinner_size: str):
    return ui.card(
        ui.busy_indicators.options(
            spinner_type=spinner_type,
            spinner_color=spinner_color,
            spinner_size=spinner_size,
        ),
        ui.card_header("Spinner: " + spinner_type),
        ui.output_plot("plot"),
    )


@module.server
def card_server(
    input: Inputs, output: Outputs, session: Session, rerender: Callable[[], object]
):
    @render.plot
    def plot():
        rerender()
        time.sleep(0.5)
        # Lazy load matplotlib and draw a simple plot without seaborn/numpy to optimize startup
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        ax.plot([0, 100], [0, 100])
        return fig


# -- Main app --
app_ui = ui.page_fillable(
    ui.busy_indicators.options(
        pulse_background="linear-gradient(45deg, blue, red)",
        pulse_height="100px",
        pulse_speed="4s",
    ),
    # ui.busy_indicators.use(spinners=False, pulse=True),
    ui.input_radio_buttons(
        "busy_indicator_type",
        "Choose the indicator type",
        ["spinners", "pulse"],
        inline=True,
    ),
    ui.input_task_button("rerender", "Re-render"),
    ui.output_text_verbatim("counter", placeholder=True),
    ui.layout_columns(
        card_ui("ring", "ring", "red", "10px"),
        card_ui("bars", "bars", "green", "20px"),
        card_ui("dots", "dots", "blue", "30px"),
        card_ui("pulse", "pulse", "olive", "50px"),
        col_widths=6,
    ),
    ui.output_ui("indicator_types_ui"),
)


def server(input: Inputs, output: Outputs, session: Session):

    @reactive.calc
    @reactive.event(input.rerender, ignore_none=False)
    def rerender():
        return input.rerender()

    card_server("ring", rerender=rerender)
    card_server("bars", rerender=rerender)
    card_server("dots", rerender=rerender)
    card_server("pulse", rerender=rerender)

    @render.ui
    def indicator_types_ui():
        selected_busy_indicator_type = input.busy_indicator_type()
        return ui.busy_indicators.use(
            spinners=(selected_busy_indicator_type == "spinners"),
            pulse=(selected_busy_indicator_type != "spinners"),
        )

    @render.text
    def counter():
        return str(rerender())


app = App(app_ui, server)
