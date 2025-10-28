from shiny import App, Inputs, Outputs, Session, reactive, render, ui

app_ui = ui.page_fluid(
    ui.h4("Toast Test App"),
    ui.input_action_button("show_basic", "Show Basic Toast"),
    ui.input_action_button("show_success", "Show Success Toast"),
    ui.input_action_button("show_warning", "Show Warning Toast"),
    ui.input_action_button("show_error", "Show Error Toast"),
    ui.input_action_button("show_with_header", "Show Toast with Header"),
    ui.input_action_button("show_top_left", "Show Top Left Toast"),
    ui.input_action_button("show_bottom_right", "Show Bottom Right Toast"),
    ui.input_action_button("show_persistent", "Show Persistent Toast"),
    ui.input_action_button("hide_toast_btn", "Hide Toast"),
    ui.output_text("toast_id_output"),
)


def server(input: Inputs, output: Outputs, session: Session):
    current_toast_id = reactive.value("")

    @reactive.effect
    @reactive.event(input.show_basic)
    def _():
        id = ui.show_toast("This is a basic toast notification", id="basic-toast")
        current_toast_id.set(id)

    @reactive.effect
    @reactive.event(input.show_success)
    def _():
        id = ui.show_toast(
            ui.toast(
                "Operation completed successfully!",
                type="success",
                header="Success",
                id="success-toast",
            )
        )
        current_toast_id.set(id)

    @reactive.effect
    @reactive.event(input.show_warning)
    def _():
        id = ui.show_toast(
            ui.toast(
                "Please review the warnings.",
                type="warning",
                header="Warning",
                id="warning-toast",
            )
        )
        current_toast_id.set(id)

    @reactive.effect
    @reactive.event(input.show_error)
    def _():
        id = ui.show_toast(
            ui.toast(
                "An error occurred.",
                type="error",
                header="Error",
                id="error-toast",
            )
        )
        current_toast_id.set(id)

    @reactive.effect
    @reactive.event(input.show_with_header)
    def _():
        id = ui.show_toast(
            ui.toast(
                "This toast has a structured header.",
                header=ui.toast_header(
                    "Update Available", icon=ui.tags.i(class_="bi bi-download")
                ),
                id="header-toast",
            )
        )
        current_toast_id.set(id)

    @reactive.effect
    @reactive.event(input.show_top_left)
    def _():
        id = ui.show_toast(
            ui.toast(
                "This appears in top left.",
                position="top-left",
                id="top-left-toast",
            )
        )
        current_toast_id.set(id)

    @reactive.effect
    @reactive.event(input.show_bottom_right)
    def _():
        id = ui.show_toast(
            ui.toast(
                "This appears in bottom right.",
                position="bottom-right",
                id="bottom-right-toast",
            )
        )
        current_toast_id.set(id)

    @reactive.effect
    @reactive.event(input.show_persistent)
    def _():
        id = ui.show_toast(
            ui.toast(
                "This toast will not auto-hide.",
                duration=None,
                header="Persistent",
                id="persistent-toast",
            )
        )
        current_toast_id.set(id)

    @reactive.effect
    @reactive.event(input.hide_toast_btn)
    def _():
        if current_toast_id():
            ui.hide_toast(current_toast_id())

    @output
    @render.text
    def toast_id_output():
        return f"Last toast ID: {current_toast_id()}"


app = App(app_ui, server)
