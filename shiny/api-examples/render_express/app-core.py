from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.input_text("name", "Name", "Socrates"),
    ui.input_text("years", "Years", "470-399 BC"),
    ui.output_ui("person"),
)


def server(input, output, session):

    @render.express
    def person():
        from shiny.express import ui

        with ui.card(class_="mt-3"):
            ui.h3(input.name())
            input.years()


app = App(app_ui, server)
