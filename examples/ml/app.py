import json

from shiny import App, Inputs, Outputs, Session, render, ui

app_ui = ui.page_fluid(
    ui.layout_sidebar(
        ui.panel_sidebar(
            ui.input_slider("lion", "Lion value:", min=0, max=100, value=60, step=1),
        ),
        ui.panel_main(
            ui.h3("Dynamic output, display_winner=True"),
            ui.ml.output_classification_label(
                "label1",
                display_winner=True,
            ),
            ui.h3("Static output, display_winner=True", style="margin-top: 3rem;"),
            ui.ml.output_classification_label(
                "label2",
                value={
                    "Tigers": 32,
                    "Lions": 60,
                    "Bears": 15,
                },
                display_winner=True,
            ),
            ui.h3("Static output, sort=False"),
            ui.ml.output_classification_label(
                "label3",
                value={
                    "Tigers": 32,
                    "Lions": 60,
                    "Bears": 15,
                },
                sort=False,
            ),
        ),
    )
)


def server(input: Inputs, output: Outputs, session: Session):
    @output
    @render.ml.classification_label
    def label1():
        return {
            "Tigers": 32,
            "Lions": input.lion(),
            "Bears": 15,
        }


app = App(app_ui, server)
