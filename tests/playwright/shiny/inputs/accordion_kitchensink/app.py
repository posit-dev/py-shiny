from faicons import icon_svg

from shiny import App, Inputs, ui

app_ui = ui.page_fluid(
    ui.h1("Accordion Kitchensink"),
    ui.accordion(
        ui.accordion_panel(
            "Panel 1",
            ui.p("This is the content of Panel 1"),
            value="panel1",
        ),
        ui.accordion_panel(
            "Panel 2",
            ui.p("This is the content of Panel 2"),
            icon=icon_svg("trash-arrow-up"),
            value="panel2",
        ),
        id="accordion_1",
        width="600px",
        height="300px",
        multiple=False,
        class_="bg-light",
    ),
    ui.accordion(
        ui.accordion_panel(
            "Panel 3",
            ui.p("This is the content of Panel 3"),
            value="panel3",
        ),
        ui.accordion_panel(
            "Panel 4",
            ui.p("This is the content of Panel 4"),
            value="panel4",
        ),
        id="accordion_2",
        multiple=True,
    ),
)


def server(input: Inputs):
    pass


app = App(app_ui, server)
