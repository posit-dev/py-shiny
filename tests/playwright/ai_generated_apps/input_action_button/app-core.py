from shiny import App, render, ui

# Create the UI
app_ui = ui.page_fluid(
    # Add Font Awesome CSS in the head
    ui.tags.head(
        ui.tags.link(
            rel="stylesheet",
            href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/css/all.min.css",
        )
    ),
    # Main layout
    ui.layout_column_wrap(
        ui.card(
            ui.card_header("Action Button Examples"),
            # Basic button with width parameter
            ui.input_action_button(id="btn1", label="Basic Button", width="200px"),
            ui.br(),  # Add spacing
            # Button with icon and disabled state
            ui.input_action_button(
                id="btn2",
                label="Disabled Button with Icon",
                icon=ui.tags.i(class_="fa-solid fa-shield-halved"),
                disabled=True,
            ),
            ui.br(),  # Add spacing
            # Button with custom class and style attributes
            ui.input_action_button(
                id="btn3",
                label="Styled Button",
                class_="btn-success",
                style="margin-top: 20px;",
            ),
        ),
        # Card for displaying results
        ui.card(
            ui.card_header("Click Counts"),
            ui.output_text("click_counts"),
        ),
        width="100%",
    ),
)


# Define the server
def server(input, output, session):
    @output
    @render.text
    def click_counts():
        return (
            f"Button 1 clicks: {input.btn1() or 0}\n"
            f"Button 2 clicks: {input.btn2() or 0}\n"
            f"Button 3 clicks: {input.btn3() or 0}"
        )


# Create and return the app
app = App(app_ui, server)
