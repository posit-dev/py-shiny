from icons import gear_fill

from shiny import App, Inputs, Outputs, Session, render, ui

app_ui = ui.page_fluid(
    ui.popover(
        ui.input_action_button("btn", "A button", class_="mt-3"),
        "A popover with more context and information than should be used in a tooltip.",
        "You can even have multiple DOM elements in a popover!",
        id="btn_popover",
    ),
    ui.hr(),
    ui.card(
        ui.card_header(
            "Plot title (Click the gear to change variables)",
            ui.popover(
                ui.span(
                    gear_fill,
                    style="position:absolute; top: 5px; right: 7px;",
                ),
                "Put dropdowns here to alter your plot!",
                ui.input_selectize("x", "X", ["x1", "x2", "x3"]),
                ui.input_selectize("y", "Y", ["y1", "y2", "y3"]),
                placement="right",
                id="card_popover",
            ),
        ),
        ui.output_text_verbatim("plot_txt", placeholder=True),
    ),
)


def server(input: Inputs, output: Outputs, session: Session):
    @render.text
    def plot_txt():
        return f"<Making plot using x: {input.x()} and y: {input.y()}>"


app = App(app_ui, server=server)
