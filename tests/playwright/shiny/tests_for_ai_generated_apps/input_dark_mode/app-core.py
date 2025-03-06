from shiny import App, render, ui

# Define the UI
app_ui = ui.page_fillable(
    # Add Font Awesome CSS in head
    ui.tags.head(
        ui.tags.link(
            rel="stylesheet",
            href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css",
        )
    ),
    # Create layout with sidebar
    ui.layout_sidebar(
        # Sidebar contents
        ui.sidebar(
            ui.input_dark_mode(id="mode", mode="light"),
        ),
        # Main panel contents
        ui.card(
            ui.card_header("Dark Mode Example"),
            ui.output_text("current_mode"),
            ui.p("This is a demonstration of dark mode functionality."),
            ui.div(
                ui.tags.i(class_="fa-solid fa-moon", style="font-size: 2rem;"),
                ui.span(" Dark Mode Toggle Example", class_="ms-2"),
                class_="mt-3",
            ),
        ),
    ),
)


# Define the server
def server(input, output, session):
    @render.text
    def current_mode():
        return f"Current mode: {input.mode()}"


# Create the app
app = App(app_ui, server)
