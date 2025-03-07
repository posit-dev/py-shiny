from shiny import App, reactive, render, ui

# Define the UI
app_ui = ui.page_fillable(
    # Add Font Awesome CSS in the head section
    ui.tags.head(
        ui.tags.link(
            rel="stylesheet",
            href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/css/all.min.css",
        )
    ),
    # Create a card to contain our task button and status
    ui.card(
        ui.card_header("Task Button Demo"),
        # Define the task button
        ui.input_task_button(
            id="task_btn",
            label="Run Task",
            icon=ui.tags.i(class_="fa-solid fa-play"),
            label_busy="Processing...",
            icon_busy=ui.tags.i(class_="fa-solid fa-spinner fa-spin"),
            class_="btn-primary m-3",
        ),
        ui.output_text("task_status"),
        height="300px",
    ),
)


# Define the server
def server(input, output, session):
    @output
    @render.text
    def task_status():
        count = input.task_btn()
        if count == 0:
            return "Task hasn't started yet"
        return f"Task has been run {count} times"

    @reactive.effect
    @reactive.event(input.task_btn)
    def handle_task():
        import time

        # Simulate a long-running task
        time.sleep(2)


# Create and return the app
app = App(app_ui, server)
