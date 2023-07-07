import shinyswatch
from htmltools import tags

from shiny import App, module, reactive, render, ui

app_ui = ui.page_fixed(
    {"class": "my-5"},
    tags.style(
        """
        .row {
            border-bottom: 1px solid #eeeeee;
            border-top: 1px solid #eeeeee;
            margin-top: -1px;
            padding: 20px 10px;
            align-items: center;
        }
        .row p {
        margin-bottom: 0px;
        }
        """
    ),
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
            where="afterBegin",
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
    out = ui.output_ui("button_row")
    return out


@module.server
def task_server(input, output, session, remove_id, task_list, text):
    finished = reactive.Value(True)

    @output
    @render.ui
    def button_row():
        if finished():
            button_text = "finish"
            button_class = "btn-default"
            text_style = ""
        else:
            button_text = "clear"
            button_class = "btn-warning"
            text_style = "text-decoration: line-through"

        out = ui.row(
            {"id": remove_id, "style": "margin: 10px, border: 1px solid #ddd"},
            ui.column(
                4,
                ui.input_action_button(
                    button_text, button_text.capitalize(), class_=button_class
                ),
            ),
            ui.column(
                8,
                ui.p(text, style=text_style),
            ),
        )
        return out

    @reactive.Effect
    @reactive.event(input.finish)
    def finish_task():
        task_list.set(task_list.get() + 1)
        finished.set(False)

    @reactive.Effect
    @reactive.event(input.clear)
    def clear_task():
        ui.remove_ui(selector=f"div#{remove_id}")


app = App(app_ui, server)
