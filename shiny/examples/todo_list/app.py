import shinyswatch
from htmltools import css

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

        finish = task_server(id, text=input.todo_input_text())

        # Defining a nested reactive effect like this might feel a bit funny but it's the
        # correct pattern in this case. We are reacting to the `finish`
        # event within the `add` closure, so nesting the reactive effects
        # means that we don't have to worry about conflicting with
        # finish events from other task elements.
        @reactive.Effect
        @reactive.event(finish)
        def iterate_counter():
            finished_tasks.set(finished_tasks.get() + 1)

        ui.update_text("todo_input_text", value="")


# Modules to define the rows


@module.ui
def task_ui():
    return ui.output_ui("button_row")


@module.server
def task_server(input, output, session, text):
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
            class_="mt-3 p-3 border align-items-center",
            style=css(text_decoration="line-through" if finished() else None),
        )

    @reactive.Effect
    @reactive.event(input.finish)
    def finish_task():
        finished.set(True)

    @reactive.Effect
    @reactive.event(input.clear)
    def clear_task():
        ui.remove_ui(selector=f"div#{session.ns('button_row')}")

        # Since remove_ui only removes the HTML the reactive effects will be held
        # in memory unless they're explicitly destroyed. This isn't a big
        # deal because they're very small, but it's good to clean them up.
        finish_task.destroy()
        clear_task.destroy()

    # Returning the input.finish button to the parent scope allows us
    # to react to it in the parent context to keep track of the number of
    # completed tasks.
    #
    # This is a good pattern because it makes the module more general.
    # The same module can be used by different applications which may
    # do different things when the task is completed.
    return input.finish


app = App(app_ui, server)
