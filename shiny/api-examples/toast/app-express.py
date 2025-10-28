from shiny import reactive
from shiny.express import input, ui

ui.h4("Toast Notification Examples")

with ui.layout_columns(col_widths=[6, 6, 6, 6]):
    with ui.card():
        ui.card_header("Basic Toasts")
        ui.input_action_button("show_basic", "Show Basic Toast")
        ui.input_action_button("show_header", "Show with Header")
        ui.input_action_button("show_icon", "Show with Icon Header")

    with ui.card():
        ui.card_header("Toast Types")
        ui.input_action_button("show_success", "Success")
        ui.input_action_button("show_warning", "Warning")
        ui.input_action_button("show_error", "Error")
        ui.input_action_button("show_info", "Info")

    with ui.card():
        ui.card_header("Positions")
        ui.input_action_button("show_top_left", "Top Left")
        ui.input_action_button("show_top_center", "Top Center")
        ui.input_action_button("show_bottom_right", "Bottom Right")

    with ui.card():
        ui.card_header("Duration & Control")
        ui.input_action_button("show_persistent", "Persistent (No Auto-hide)")
        ui.input_action_button("show_quick", "Quick (2 seconds)")
        ui.input_action_button("hide_all", "Hide Last Toast")

toast_ids: list[str] = []


@reactive.effect
@reactive.event(input.show_basic)
def _():
    id = ui.show_toast("This is a basic toast notification!")
    toast_ids.append(id)


@reactive.effect
@reactive.event(input.show_header)
def _():
    from shiny.ui import toast

    id = ui.show_toast(
        toast(
            "This toast has a header with additional context.",
            header="Important Message",
        )
    )
    toast_ids.append(id)


@reactive.effect
@reactive.event(input.show_icon)
def _():
    from shiny.ui import toast, toast_header

    id = ui.show_toast(
        toast(
            "This header includes an icon and status.",
            header=toast_header(
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
    from shiny.ui import toast

    id = ui.show_toast(
        toast(
            "Operation completed successfully!",
            type="success",
            header="Success",
        )
    )
    toast_ids.append(id)


@reactive.effect
@reactive.event(input.show_warning)
def _():
    from shiny.ui import toast

    id = ui.show_toast(
        toast(
            "Please review the warnings before continuing.",
            type="warning",
            header="Warning",
        )
    )
    toast_ids.append(id)


@reactive.effect
@reactive.event(input.show_error)
def _():
    from shiny.ui import toast

    id = ui.show_toast(
        toast(
            "An error occurred. Please try again.",
            type="error",
            header="Error",
        )
    )
    toast_ids.append(id)


@reactive.effect
@reactive.event(input.show_info)
def _():
    from shiny.ui import toast

    id = ui.show_toast(
        toast(
            "Here's some helpful information.",
            type="info",
            header="Info",
        )
    )
    toast_ids.append(id)


@reactive.effect
@reactive.event(input.show_top_left)
def _():
    from shiny.ui import toast

    id = ui.show_toast(
        toast(
            "This toast appears in the top left corner.",
            position="top-left",
        )
    )
    toast_ids.append(id)


@reactive.effect
@reactive.event(input.show_top_center)
def _():
    from shiny.ui import toast

    id = ui.show_toast(
        toast(
            "This toast appears at the top center.",
            position="top-center",
        )
    )
    toast_ids.append(id)


@reactive.effect
@reactive.event(input.show_bottom_right)
def _():
    from shiny.ui import toast

    id = ui.show_toast(
        toast(
            "This toast appears in the bottom right (default).",
            position="bottom-right",
        )
    )
    toast_ids.append(id)


@reactive.effect
@reactive.event(input.show_persistent)
def _():
    from shiny.ui import toast

    id = ui.show_toast(
        toast(
            "This toast will not auto-hide. Click the X to close.",
            duration=None,
            header="Persistent Toast",
        )
    )
    toast_ids.append(id)


@reactive.effect
@reactive.event(input.show_quick)
def _():
    from shiny.ui import toast

    id = ui.show_toast(
        toast(
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
