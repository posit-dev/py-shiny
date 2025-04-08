from shiny.express import input, render, ui

# Page options for the app
ui.page_opts(fillable=True)

# Create a navset_pill with all possible parameters
with ui.navset_pill(id="pills"):
    # Panel A
    with ui.nav_panel("A"):
        "This is content for Panel A"
        ui.input_slider("n1", "N1", min=0, max=100, value=20)

        @render.text
        def panel_a_text():
            return f"Value of n1: {input.n1()}"

    # Panel B
    with ui.nav_panel("B"):
        "This is content for Panel B"
        ui.input_numeric("n2", "N2", value=10)

        @render.text
        def panel_b_text():
            return f"Value of n2: {input.n2()}"

    # Panel C
    with ui.nav_panel("C"):
        "This is content for Panel C"
        ui.input_text("txt", "Enter text", "Hello")

        @render.text
        def panel_c_text():
            return f"You entered: {input.txt()}"


# Show which panel is currently selected
@render.text
def selected_panel():
    return f"Currently selected panel: {input.pills()}"
