from shiny.express import input, render, ui

# Add Font Awesome CSS in the head section first
ui.head_content(
    ui.HTML(
        '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/css/all.min.css">'
    )
)

ui.page_opts(fillable=True)

with ui.card():
    with ui.accordion(id="acc", open=True, multiple=True):
        # Panel with just title
        with ui.accordion_panel("Basic Panel"):
            ui.markdown("This is a basic panel with just a title parameter")

        # Panel with title and value
        with ui.accordion_panel("Panel with Value", value="panel2"):
            ui.markdown("This panel has both a title and a value parameter")

        # Panel with title, value, and icon
        with ui.accordion_panel(
            "Panel with Icon",
            value="panel3",
            icon=ui.tags.i(
                class_="fa-solid fa-shield-halved", style="font-size: 1rem;"
            ),
        ):
            ui.markdown("This panel includes an icon parameter using Font Awesome")

        # Panel with title, value, icon, and custom attributes
        with ui.accordion_panel(
            "Panel with Custom Attributes",
            value="panel4",
            icon=ui.tags.i(class_="fa-solid fa-star", style="font-size: 1rem;"),
            class_="custom-panel",
            style="background-color: #f8f9fa;",
        ):
            ui.markdown("This panel demonstrates custom attributes (class and style)")


# Show which panel is currently selected
@render.text
def selected_panel():
    return f"Currently selected panel: {input.acc()}"
