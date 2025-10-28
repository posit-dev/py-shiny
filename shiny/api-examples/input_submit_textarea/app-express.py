import time

from shiny.express import input, render, ui

ui.input_submit_textarea("text", placeholder="Enter some input...")


@render.text
def value():
    if "text" in input:
        # Simulate processing time
        time.sleep(2)
        return f"You entered: {input.text()}"
    else:
        return "Submit some input to see it here."
