from shiny import App, ui

app_ui = ui.page_fluid(
    ui.h2("Icon Examples"),
    ui.layout_columns(
        ui.card(
            ui.card_header("Bootstrap Icons"),
            ui.p("Bootstrap Icons work out of the box:"),
            ui.input_action_button(
                "btn_bs", "Click me", icon=ui.icon("star", lib="bs")
            ),
            ui.br(),
            ui.br(),
            ui.p("Different sizes:"),
            ui.icon("gear", lib="bs", size="1em"),
            ui.icon("gear", lib="bs", size="2em"),
            ui.icon("gear", lib="bs", size="3em"),
        ),
        ui.card(
            ui.card_header("Accessible Icons"),
            ui.p("Semantic icon with title for screen readers:"),
            ui.icon(
                "exclamation-triangle",
                lib="bs",
                size="2em",
                title="Warning",
                a11y="semantic",
            ),
        ),
    ),
)


def server(input, output, session):
    pass


app = App(app_ui, server)
