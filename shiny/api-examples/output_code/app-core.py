from shiny import App, Inputs, Outputs, Session, render, ui

app_ui = ui.page_fluid(
    ui.input_text_area(
        "source",
        "Enter code to display below:",
        "print('Hello, Shiny!')\nfor i in range(3):\n    print(i)",
        rows=8,
    ),
    ui.card(
        ui.output_code("code_default"),
    ),
    ui.card(
        ui.output_code("code_no_placeholder", placeholder=False),
    ),
)


def server(input: Inputs, output: Outputs, session: Session):
    @render.code
    def code_default():
        return input.source()

    @render.code
    def code_no_placeholder():
        return input.source()


app = App(app_ui, server)
