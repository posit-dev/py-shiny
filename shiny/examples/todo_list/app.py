import shinyswatch
from htmltools import tags

from shiny import App, module, reactive, render, ui

app_ui = ui.page_fixed(
    {"class": "my-5"},
    shinyswatch.theme.minty(),
    ui.panel_title("Shiny TodoMVC"),
    ui.layout_sidebar(
        ui.panel_sidebar(
            ui.input_text("todo_input_text", "", placeholder="Todo text"),
            ui.input_action_button("add", "Add to-do"),
        ),
        ui.panel_main(
            ui.output_text("cleared_tasks"),
            ui.div(id="tasks", style="margin-top: 0.5em"),
        ),
    ),
)


def server(input, output, session):
    finished_tasks = reactive.Value(0)
    task_counter = reactive.Value(0)

    @output
    @render.text
    def cleared_tasks():
        return f"Finished tasks: {finished_tasks()}"

    @reactive.Effect
    @reactive.event(input.add)
    def add():
        counter = task_counter.get() + 1
        task_counter.set(counter)
        id = "task_" + str(counter)
        ui.insert_ui(
            selector="#tasks",
            where="beforeEnd",
            ui=task_ui(id),
        )

        # Since we want the action button inside the module to update
        # the finished_tasks global counter, we need to pass the reactive values list
        # down to the module function.
        task_server(
            id, remove_id=id, task_list=finished_tasks, text=input.todo_input_text()
        )
        ui.update_text("todo_input_text", value="")


# Modules to define the rows


@module.ui
def task_ui():
    return ui.output_ui("button_row")


@module.server
def task_server(input, output, session, remove_id, task_list, text):
    finished = reactive.Value(False)

    @output
    @render.ui
    def button_row():
        button = None
        if finished():
            button = ui.input_action_button("clear", "Clear", class_="btn-warning")
        else:
            button = ui.input_action_button("finish", "Finish", class_="btn-default")

        return ui.row(
            ui.column(4, button),
            ui.column(8, text),
            id=remove_id,
            class_="mt-3 p-3 border align-items-center",
            style=css(text_decoration="line-through" if finished() else None),
        )

    @reactive.Effect
    @reactive.event(input.finish)
    def finish_task():
        task_list.set(task_list.get() + 1)
        finished.set(True)

    @reactive.Effect
    @reactive.event(input.clear)
    def clear_task():
        ui.remove_ui(selector=f"div#{remove_id}")


app = App(app_ui, server)
