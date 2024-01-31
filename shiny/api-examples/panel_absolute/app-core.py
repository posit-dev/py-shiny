from shiny import App, Inputs, ui

app_ui = ui.page_fluid(
    ui.panel_title("A basic absolute panel example", "Demo"),
    ui.panel_absolute(
        ui.panel_well(
            "Drag me around!", ui.input_slider("n", "N", min=0, max=100, value=20)
        ),
        draggable=True,
        width="300px",
        right="50px",
        top="25%",
    ),
)


def server(input: Inputs):
    pass


app = App(app_ui, server)
