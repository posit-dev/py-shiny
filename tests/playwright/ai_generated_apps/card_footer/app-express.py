from shiny.express import input, render, ui

# Set page options including title
ui.page_opts(title="Card Footer Demo", fillable=True)

# Create a card with footer to demonstrate basic parameters
with ui.card(full_screen=True, height="300px", id="card1"):
    ui.card_header("Basic Card with Header")
    "This is a basic card with header and footer"
    ui.card_footer("Footer content", class_="bg-light")

# Create another card to show different content types in footer
with ui.card(full_screen=True, height="600px", id="card2"):
    ui.card_header("Card with Complex Footer")
    "This card shows different types of content in footer"

    with ui.card_footer():
        ui.HTML("<strong>Bold text</strong>")
        ui.tags.span(" | ", style="margin: 0 10px;")
        ui.tags.em("Emphasized text")
        ui.tags.span(" | ", style="margin: 0 10px;")
        ui.tags.span("Regular text", style="color: green;")

# Add a third card with interactive elements in footer
with ui.card(full_screen=True, height="400px", id="card3"):
    ui.card_header("Card with Interactive Footer")
    "This card has interactive elements in its footer"

    with ui.card_footer(class_="d-flex justify-content-between align-items-center"):
        ui.input_action_button("btn", "Click Me", class_="btn-primary")

        @render.text
        def click_count():
            if not input.btn():
                return "No clicks yet"
            return f"Clicked {input.btn()} times"
