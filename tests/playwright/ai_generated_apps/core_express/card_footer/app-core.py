from shiny import App, render, ui

app_ui = ui.page_fillable(
    # First card with basic footer
    ui.card(
        ui.card_header("Basic Card with Header"),
        "This is a basic card with header and footer",
        ui.card_footer("Footer content", class_="bg-light"),
        full_screen=True,
        height="300px",
        id="card1",
    ),
    # Second card with complex footer
    ui.card(
        ui.card_header("Card with Complex Footer"),
        "This card shows different types of content in footer",
        ui.card_footer(
            ui.HTML("<strong>Bold text</strong>"),
            ui.tags.span(" | ", style="margin: 0 10px;"),
            ui.tags.em("Emphasized text"),
            ui.tags.span(" | ", style="margin: 0 10px;"),
            ui.tags.span("Regular text", style="color: green;"),
        ),
        full_screen=True,
        height="600px",
        id="card2",
    ),
    # Third card with interactive footer
    ui.card(
        ui.card_header("Card with Interactive Footer"),
        "This card has interactive elements in its footer",
        ui.card_footer(
            ui.input_action_button("btn", "Click Me", class_="btn-primary"),
            ui.output_text("click_count"),
            class_="d-flex justify-content-between align-items-center",
        ),
        full_screen=True,
        height="400px",
        id="card3",
    ),
)


def server(input, output, session):
    @render.text
    def click_count():
        if not input.btn():
            return "No clicks yet"
        return f"Clicked {input.btn()} times"


app = App(app_ui, server)
