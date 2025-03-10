from shiny.express import input, render, ui

# Add Font Awesome CSS in the head section
ui.head_content(
    ui.HTML(
        '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/css/all.min.css">'
    )
)

# Set page title
ui.page_opts(fillable=True)

with ui.layout_column_wrap(width=1 / 2):
    # Create a card to hold the action link
    with ui.card(full_screen=True, height="300px", id="card1"):
        ui.card_header("Action Link Demo")

        # Create an action link with an icon
        ui.input_action_link(
            id="demo_link",
            label="Click Me!",
            icon=ui.tags.i(class_="fa-solid fa-shield-halved"),
        )

        # Display the click count
        @render.text
        def link_clicks():
            count = input.demo_link() or 0
            return f"The link has been clicked {count} times"

    # Create another card to show reactive behavior
    with ui.card(full_screen=True, height="300px", id="card2"):
        ui.card_header("Click History")

        @render.text
        def click_history():
            count = input.demo_link() or 0
            if count == 0:
                return "No clicks yet!"
            elif count == 1:
                return "First click recorded!"
            else:
                return f"You've clicked {count} times. Keep going!"
