from shiny import reactive
from shiny.express import input, render, ui

# Page options for basic styling
ui.page_opts(fillable=True)

# Add Font Awesome CSS in the head section
ui.head_content(
    ui.HTML(
        '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/css/all.min.css">'
    )
)

# Create a card to contain our task button and status
with ui.card(height="300px"):
    ui.card_header("Task Button Demo")

    # Define the task button
    ui.input_task_button(
        id="task_btn",
        label="Run Task",
        icon=ui.tags.i(class_="fa-solid fa-play"),
        label_busy="Processing...",
        icon_busy=ui.tags.i(class_="fa-solid fa-spinner fa-spin"),
        class_="btn-primary m-3",
    )

    @render.text
    def task_status():
        count = input.task_btn()
        if count == 0:
            return "Task hasn't started yet"
        return f"Task has been run {count} times"


# Effect to handle the task
@reactive.effect
@reactive.event(input.task_btn)
def handle_task():
    import time

    # Simulate a long-running task
    time.sleep(2)
