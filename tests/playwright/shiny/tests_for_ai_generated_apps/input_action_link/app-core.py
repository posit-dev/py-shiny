from shiny import App, render, ui

# Define the UI
app_ui = ui.page_fillable(
    # Add Font Awesome CSS in the head section
    ui.tags.head(
        ui.tags.link(
            rel="stylesheet",
            href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/css/all.min.css",
        )
    ),
    # Create layout with columns
    ui.layout_column_wrap(
        # First card
        ui.card(
            ui.card_header("Action Link Demo"),
            # Create an action link with an icon
            ui.input_action_link(
                id="demo_link",
                label="Click Me!",
                icon=ui.tags.i(class_="fa-solid fa-shield-halved"),
            ),
            ui.output_text("link_clicks"),
            full_screen=True,
            height="300px",
            id="card1",
        ),
        # Second card
        ui.card(
            ui.card_header("Click History"),
            ui.output_text("click_history"),
            full_screen=True,
            height="300px",
            id="card2",
        ),
        width=1 / 2,
    ),
)


# Define the server
def server(input, output, session):
    @output
    @render.text
    def link_clicks():
        count = input.demo_link() or 0
        return f"The link has been clicked {count} times"

    @output
    @render.text
    def click_history():
        count = input.demo_link() or 0
        if count == 0:
            return "No clicks yet!"
        elif count == 1:
            return "First click recorded!"
        else:
            return f"You've clicked {count} times. Keep going!"


# Create and return the app
app = App(app_ui, server)
