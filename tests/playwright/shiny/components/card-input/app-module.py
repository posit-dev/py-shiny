from shiny import App, Inputs, Outputs, Session, module, render, ui


@module.ui
def ui_card():
    return ui.card(
        ui.card_header("Hello, card!"),
        "A regular full-screenable card.",
        id="thing",
        full_screen=True,
    )


@module.ui
def ui_value_box():
    return ui.value_box(
        "Hello, value box!",
        "$1,234,567",
        id="thing",
        full_screen=True,
        showcase=ui.span("$", class_="fs-1"),
    )


@module.server
def card_server(input: Inputs, output: Outputs, session: Session):
    return input.thing_full_screen


app_ui = ui.page_fluid(
    ui_card("card"),
    ui_value_box("value_box"),
    ui.output_code("out_card"),
    ui.output_code("out_value_box"),
)


def server(input: Inputs):
    my_card = card_server("card")
    my_value_box = card_server("value_box")

    @render.code()
    def out_card():
        return my_card()

    @render.code()
    def out_value_box():
        return my_value_box()


app = App(app_ui, server)
