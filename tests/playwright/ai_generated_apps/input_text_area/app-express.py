from shiny.express import input, render, ui

ui.page_opts(full_width=True)

ui.tags.head(
    ui.tags.title("Text Area Demo"),
)
# Create a text area with all possible parameters
ui.input_text_area(
    id="text_input",
    label="Enter your text:",
    value="This is some default text.\nIt has multiple lines.\nYou can edit it!",
    width="500px",
    height="200px",
    cols=50,
    rows=8,
    placeholder="Type something here...",
    resize="both",
    autoresize=True,
    spellcheck="true",
)

# Add some spacing
ui.br()
ui.br()

# Add a header for the output
ui.h4("Output:")


# Display the input value in a pre-formatted text block
@render.text
def show_text():
    return f"You entered:\n{input.text_input()}"
