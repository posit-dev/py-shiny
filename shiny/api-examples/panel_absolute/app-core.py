from shiny import App, Inputs, Outputs, Session, ui

app_ui = ui.page_fluid(
    ui.panel_title("A basic absolute panel example", "Demo"),
    ui.panel_absolute(
        ui.card(
            ui.card_header("Drag me around!"),
            ui.input_slider("n", "N", min=0, max=100, value=20),
        ),
        draggable=True,
        width="300px",
        right="50px",
        top="25%",
    ),
)


def server(input: Inputs, output: Outputs, session: Session):
    pass


app = App(app_ui, server)
