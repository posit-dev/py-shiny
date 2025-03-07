from shiny.express import input, render, ui

# Set page options for a clean layout
ui.page_opts(fillable=True)

# Create a card to contain the input and output
with ui.card():
    ui.card_header("Text Input Example")

    # Create text input with all possible parameters
    ui.input_text(
        id="demo_text",  # Required: unique identifier
        label="Demo Text Input",  # Required: label text
        value="Initial value",  # Optional: starting value
        width="300px",  # Optional: CSS width
        placeholder="Enter text here",  # Optional: hint text
        autocomplete="off",  # Optional: browser autocomplete behavior
        spellcheck="true",  # Optional: browser spellcheck behavior
    )

    # Add some spacing
    ui.hr()

    # Display area for the current value
    @render.text
    def current_value():
        return f"Current value: {input.demo_text()}"
