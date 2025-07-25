from shiny import App, module, render, ui


@module.ui
def my_module_ui():
    """Defines the UI elements for the module with multiple text inputs."""
    return ui.div(
        ui.h2("My Module"),
        ui.input_text("text_input_1", "Enter the first text:"),
        ui.input_text("text_input_2", "Enter the second text:"),  # Second text input
        ui.output_text("text_output"),
    )


@module.server
def my_module_server(input, output, session):
    """Defines the server logic for the module."""

    @render.text
    def text_output():
        return f"You entered: {input.text_input_1()} and {input.text_input_2()}"  # Accessing both inputs


app_ui = ui.page_fluid(ui.h1("Main Application"), my_module_ui("module_instance_1"))


def server(input, output, session):
    my_module_server("module_instance_1")


app = App(app_ui, server)
