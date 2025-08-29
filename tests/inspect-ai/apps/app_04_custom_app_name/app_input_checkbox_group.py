from shiny.express import input, render, ui

# Create sample choices with HTML formatting for demonstration
choices = {
    "red": ui.span("Red", style="color: #FF0000;"),
    "green": ui.span("Green", style="color: #00AA00;"),
    "blue": ui.span("Blue", style="color: #0000AA;"),
}

with ui.card():
    ui.card_header("Color Selection Demo")

    # Using input_checkbox_group with all its parameters
    ui.input_checkbox_group(
        id="colors",  # Required: unique identifier
        label="Choose colors",  # Required: label text
        choices=choices,  # Required: choices as dict with HTML formatting
        selected=["red", "blue"],  # Optional: pre-selected values
        inline=True,  # Optional: display choices inline
        width="300px",  # Optional: CSS width
    )

    # Add some spacing
    ui.hr()

    # Simple output to show selected values
    @render.text
    def selected_colors():
        if input.colors():
            return f"You selected: {', '.join(input.colors())}"
        return "No colors selected"
