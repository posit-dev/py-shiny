from shiny.express import ui

ui.h2("Icon Examples")

with ui.layout_columns():
    with ui.card():
        ui.card_header("Bootstrap Icons")
        ui.p("Bootstrap Icons work out of the box:")
        ui.input_action_button("btn_bs", "Click me", icon=ui.icon("star", lib="bs"))
        ui.br()
        ui.br()
        ui.p("Different sizes:")
        ui.icon("gear", lib="bs", size="1em")
        ui.icon("gear", lib="bs", size="2em")
        ui.icon("gear", lib="bs", size="3em")

    with ui.card():
        ui.card_header("Accessible Icons")
        ui.p("Semantic icon with title for screen readers:")
        ui.icon(
            "exclamation-triangle",
            lib="bs",
            size="2em",
            title="Warning",
            a11y="semantic",
        )
