from shiny import App, Inputs, Outputs, Session, render, ui

app_ui = ui.page_fluid(
    ui.card(
        ui.layout_sidebar(
            ui.sidebar("Left sidebar content", id="sidebar_left"),
            ui.output_text_verbatim("state_left"),
        )
    ),
    ui.card(
        ui.layout_sidebar(
            ui.sidebar("Right sidebar content", id="sidebar_right", position="right"),
            ui.output_text_verbatim("state_right"),
        ),
    ),
    ui.card(
        ui.layout_sidebar(
            ui.sidebar("Closed sidebar content", id="sidebar_closed", open="closed"),
            ui.output_text_verbatim("state_closed"),
        )
    ),
    ui.card(
        ui.layout_sidebar(
            ui.sidebar("Always sidebar content", id="sidebar_always", open="always"),
            ui.output_text_verbatim("state_always"),
        )
    ),
)


def server(input: Inputs, output: Outputs, session: Session):
    @render.text
    def state_left():
        return f"input.sidebar_left(): {input.sidebar_left()}"

    @render.text
    def state_right():
        return f"input.sidebar_right(): {input.sidebar_right()}"

    @render.text
    def state_closed():
        return f"input.sidebar_closed(): {input.sidebar_closed()}"

    @render.text
    def state_always():
        return f"input.sidebar_always(): {input.sidebar_always()}"


app = App(app_ui, server)
