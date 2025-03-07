from shiny import App, render, ui

# Define the UI
app_ui = ui.page_fillable(
    # Create a navset_pill with all possible parameters
    ui.navset_pill(
        # Panel A
        ui.nav_panel(
            "A",
            "This is content for Panel A",
            ui.input_slider("n1", "N1", min=0, max=100, value=20),
            ui.output_text("panel_a_text"),
        ),
        # Panel B
        ui.nav_panel(
            "B",
            "This is content for Panel B",
            ui.input_numeric("n2", "N2", value=10),
            ui.output_text("panel_b_text"),
        ),
        # Panel C
        ui.nav_panel(
            "C",
            "This is content for Panel C",
            ui.input_text("txt", "Enter text", "Hello"),
            ui.output_text("panel_c_text"),
        ),
        id="pills",
    ),
    # Show which panel is currently selected
    ui.output_text("selected_panel"),
)


# Define the server
def server(input, output, session):
    @render.text
    def panel_a_text():
        return f"Value of n1: {input.n1()}"

    @render.text
    def panel_b_text():
        return f"Value of n2: {input.n2()}"

    @render.text
    def panel_c_text():
        return f"You entered: {input.txt()}"

    @render.text
    def selected_panel():
        return f"Currently selected panel: {input.pills()}"


# Create the app
app = App(app_ui, server)
