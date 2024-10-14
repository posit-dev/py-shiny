from shiny import App, ui

app_ui = ui.page_fluid(
    ui.card(
        ui.card_header("Check for header"),
        "This is the body of a card with default height w/ fullscreen",
        ui.card_footer("Check for footer"),
        full_screen=True,
        id="card1",
    ),
    ui.card(
        ui.p("This is the body without a header of a footer - No Fullscreen"),
        full_screen=False,
        id="card2",
    ),
    ui.card(
        ui.card_header("Fill is False. Fullscreen is False"),
        ui.h3("Max height and min height are set."),
        fill=False,
        max_height="500px",
        min_height="200px",
        id="card3",
    ),
)


app = App(app_ui, server=None)
