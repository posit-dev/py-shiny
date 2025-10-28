from shiny import App, Inputs, Outputs, Session, reactive, ui

app_ui = ui.page_fluid(
    ui.h4("Toast Notification Examples"),
    ui.layout_columns(
        ui.card(
            ui.card_header("Basic Toasts"),
            ui.input_action_button("show_basic", "Show Basic Toast"),
            ui.input_action_button("show_header", "Show with Header"),
            ui.input_action_button("show_icon", "Show with Icon Header"),
        ),
        ui.card(
            ui.card_header("Toast Types"),
            ui.input_action_button("show_success", "Success"),
            ui.input_action_button("show_warning", "Warning"),
            ui.input_action_button("show_error", "Error"),
            ui.input_action_button("show_info", "Info"),
        ),
        ui.card(
            ui.card_header("Positions"),
            ui.input_action_button("show_top_left", "Top Left"),
            ui.input_action_button("show_top_center", "Top Center"),
            ui.input_action_button("show_bottom_right", "Bottom Right"),
        ),
        ui.card(
            ui.card_header("Duration & Control"),
            ui.input_action_button("show_persistent", "Persistent (No Auto-hide)"),
            ui.input_action_button("show_quick", "Quick (2 seconds)"),
            ui.input_action_button("hide_all", "Hide Last Toast"),
        ),
        col_widths=[6, 6, 6, 6],
    ),
)


def server(input: Inputs, output: Outputs, session: Session):
    toast_ids: list[str] = []

    @reactive.effect
    @reactive.event(input.show_basic)
    def _():
        id = ui.show_toast("This is a basic toast notification!")
        toast_ids.append(id)

    @reactive.effect
    @reactive.event(input.show_header)
    def _():
        id = ui.show_toast(
            ui.toast(
                "This toast has a header with additional context.",
                header="Important Message",
            )
        )
        toast_ids.append(id)

    @reactive.effect
    @reactive.event(input.show_icon)
    def _():
        id = ui.show_toast(
            ui.toast(
                "This header includes an icon and status.",
                header=ui.toast_header(
                    "Update Available",
                    icon=ui.tags.i(class_="bi bi-download"),
                    status="just now",
                ),
            )
        )
        toast_ids.append(id)

    @reactive.effect
    @reactive.event(input.show_success)
    def _():
        id = ui.show_toast(
            ui.toast(
                "Operation completed successfully!",
                type="success",
                header="Success",
            )
        )
        toast_ids.append(id)

    @reactive.effect
    @reactive.event(input.show_warning)
    def _():
        id = ui.show_toast(
            ui.toast(
                "Please review the warnings before continuing.",
                type="warning",
                header="Warning",
            )
        )
        toast_ids.append(id)

    @reactive.effect
    @reactive.event(input.show_error)
    def _():
        id = ui.show_toast(
            ui.toast(
                "An error occurred. Please try again.",
                type="error",
                header="Error",
            )
        )
        toast_ids.append(id)

    @reactive.effect
    @reactive.event(input.show_info)
    def _():
        id = ui.show_toast(
            ui.toast(
                "Here's some helpful information.",
                type="info",
                header="Info",
            )
        )
        toast_ids.append(id)

    @reactive.effect
    @reactive.event(input.show_top_left)
    def _():
        id = ui.show_toast(
            ui.toast(
                "This toast appears in the top left corner.",
                position="top-left",
            )
        )
        toast_ids.append(id)

    @reactive.effect
    @reactive.event(input.show_top_center)
    def _():
        id = ui.show_toast(
            ui.toast(
                "This toast appears at the top center.",
                position="top-center",
            )
        )
        toast_ids.append(id)

    @reactive.effect
    @reactive.event(input.show_bottom_right)
    def _():
        id = ui.show_toast(
            ui.toast(
                "This toast appears in the bottom right (default).",
                position="bottom-right",
            )
        )
        toast_ids.append(id)

    @reactive.effect
    @reactive.event(input.show_persistent)
    def _():
        id = ui.show_toast(
            ui.toast(
                "This toast will not auto-hide. Click the X to close.",
                duration=None,
                header="Persistent Toast",
            )
        )
        toast_ids.append(id)

    @reactive.effect
    @reactive.event(input.show_quick)
    def _():
        id = ui.show_toast(
            ui.toast(
                "This toast will disappear in 2 seconds.",
                duration=2,
            )
        )
        toast_ids.append(id)

    @reactive.effect
    @reactive.event(input.hide_all)
    def _():
        if toast_ids:
            ui.hide_toast(toast_ids.pop())


app = App(app_ui, server, debug=True)
