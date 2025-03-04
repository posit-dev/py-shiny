from shiny.express import input, render, ui

# Add Font Awesome CSS in the head section
ui.head_content(
    ui.HTML(
        '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/css/all.min.css">'
    )
)

# Create a list of accordion panels with different configurations
with ui.accordion(id="acc_demo", open=["Panel B", "Panel D"], multiple=True):
    # Basic panel
    with ui.accordion_panel("Panel A"):
        "This is a basic accordion panel with default settings."

    # Panel with custom icon
    with ui.accordion_panel(
        "Panel B", icon=ui.HTML('<i class="fa-solid fa-star" style="color: gold;"></i>')
    ):
        "This panel has a custom star icon and is open by default."

    # Basic panel that starts closed
    with ui.accordion_panel("Panel C"):
        "This is another basic panel that starts closed."

    # Panel with longer content
    with ui.accordion_panel("Panel D"):
        ui.markdown(
            """
        This panel contains longer content to demonstrate scrolling:

        - Item 1
        - Item 2
        - Item 3

        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do
        eiusmod tempor incididunt ut labore et dolore magna aliqua.
        """
        )


# Show which panels are currently open
@render.text
def selected_panels():
    return f"Currently open panels: {input.acc_demo()}"
