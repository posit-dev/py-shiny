from shiny import App, Inputs, Outputs, Session, render, ui

app_ui = ui.page_fluid(
    ui.layout_sidebar(
        ui.panel_sidebar(
            ui.input_slider("lion", "Lion value:", min=0, max=100, value=60, step=1),
        ),
        ui.panel_main(
            ui.h3("Dynamic output, display_winner=True"),
            ui.output_ui("label1"),
            ui.h3(
                "Static output, display_winner=True, max_items=2",
                style="margin-top: 3rem;",
            ),
            ui.ml.classification_label(
                {
                    "Tigers": 32,
                    "Lions": 60,
                    "Bears": 15,
                },
                display_winner=True,
                max_items=2,
            ),
            ui.h3("Static output, sort=False"),
            ui.ml.classification_label(
                {
                    "Tigers": 32,
                    "Lions": 60,
                    "Bears": 15,
                },
                max_items=3,
                sort=False,
            ),
        ),
    )
)


def server(input: Inputs, output: Outputs, session: Session):
    @output
    @render.ui
    def label1():
        return (
            ui.ml.classification_label(
                value={
                    "Tigers": 32,
                    "Lions": input.lion(),
                    "Bears": 15,
                },
                display_winner=True,
            ),
        )


app = App(app_ui, server)
