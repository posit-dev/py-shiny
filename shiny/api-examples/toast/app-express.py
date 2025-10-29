import time

from faicons import icon_svg

from shiny import reactive
from shiny.express import input, ui
from shiny.ui import toast, toast_header

ui.page_opts(
    title=ui.tags.h2("Toast Notifications Demo", class_="h3 ps-3 pt-3 mb-0"),
    fillable=True,
    padding=0,
)

ui.input_dark_mode(class_="position-absolute top-0 end-0 p-3")

with ui.layout_column_wrap(
    width=1 / 2,
    class_="bslib-page-dashboard",
    style="background: var(--bslib-dashboard-main-bg); padding: 15px; gap: 15px",
):
    # Toast Builder Card
    with ui.card():
        ui.card_header("Toast Builder")

        with ui.card_body():
            ui.input_text_area(
                "body",
                "Body Content",
                value="This is a toast notification!",
                rows=3,
                width="100%",
            )

            with ui.layout_columns():
                with ui.div():
                    ui.input_select(
                        "type",
                        "Type (Background Color)",
                        choices={
                            "": "None (default)",
                            "primary": "Primary",
                            "secondary": "Secondary",
                            "success": "Success",
                            "info": "Info",
                            "warning": "Warning",
                            "danger": "Danger",
                            "light": "Light",
                            "dark": "Dark",
                        },
                        selected="",
                    )

                    ui.input_select(
                        "position",
                        "Position",
                        choices={
                            "top-left": "Top Left",
                            "top-center": "Top Center",
                            "top-right": "Top Right",
                            "middle-left": "Middle Left",
                            "middle-center": "Middle Center",
                            "middle-right": "Middle Right",
                            "bottom-left": "Bottom Left",
                            "bottom-center": "Bottom Center",
                            "bottom-right": "Bottom Right",
                        },
                        selected="top-right",
                    )

                    ui.input_slider(
                        "duration",
                        "Duration (seconds, 0 = disabled)",
                        min=0,
                        max=25,
                        value=5,
                        step=1,
                        ticks=False,
                    )

                    ui.input_switch("closable", "Show Close Button", value=True)

                with ui.div():
                    ui.input_switch("use_header", "Include Header", value=False)

                    with ui.panel_conditional("input.use_header"):
                        ui.input_text(
                            "header_title", "Header Title", value="Notification"
                        )
                        ui.input_select(
                            "header_icon",
                            "Icon",
                            choices={
                                "": "None",
                                "circle-check": "Check",
                                "circle-info": "Info",
                                "triangle-exclamation": "Warning",
                                "circle-xmark": "Error",
                                "star": "Star",
                                "heart": "Heart",
                                "bell": "Bell",
                                "user": "User",
                                "gear": "Cog",
                            },
                            selected="",
                        )

                    with ui.panel_conditional("!input.use_header"):
                        ui.input_select(
                            "icon_body",
                            "Icon",
                            choices={
                                "": "None",
                                "circle-check": "Check",
                                "circle-info": "Info",
                                "triangle-exclamation": "Warning",
                                "circle-xmark": "Error",
                                "star": "Star",
                                "heart": "Heart",
                                "bell": "Bell",
                                "user": "User",
                                "gear": "Settings",
                                "comments": "Chat",
                                "envelope": "Envelope",
                                "lightbulb": "Lightbulb",
                                "rocket": "Rocket",
                                "shield": "Shield",
                                "thumbs-up": "Thumbs Up",
                                "download": "Download",
                                "upload": "Upload",
                                "calendar": "Calendar",
                                "clock": "Clock",
                                "fire": "Fire",
                                "gift": "Gift",
                                "trophy": "Trophy",
                                "flag": "Flag",
                                "thumbtack": "Pin",
                            },
                        )

        with ui.card_footer(class_="hstack gap-2 justify-content-end"):
            ui.input_action_button("show_toast", "Show Toast", class_="btn-primary")
            ui.input_action_button(
                "hide_toast", "Hide Last Toast", class_="btn-secondary"
            )

    with ui.layout_column_wrap(width=1):
        # Advanced Features
        with ui.card():
            ui.card_header("Advanced Features")
            with ui.card_body():
                ui.input_action_button(
                    "show_persistent", "Show Persistent Toast", class_="mb-2 w-100"
                )
                ui.input_action_button(
                    "hide_persistent", "Hide Persistent Toast", class_="mb-2 w-100"
                )
                ui.input_action_button(
                    "show_long_duration", "Long Duration (10s)", class_="mb-2 w-100"
                )
                ui.input_action_button(
                    "show_no_close", "No Close Button", class_="mb-2 w-100"
                )
                ui.input_action_button(
                    "show_custom_header",
                    "Custom Header with Icon & Status",
                    class_="mb-2 w-100",
                )

        # Interactive Toasts
        with ui.card():
            ui.card_header("Interactive Toasts")
            with ui.card_body():
                ui.input_action_button(
                    "show_action_buttons",
                    "Toast with Action Buttons",
                    class_="mb-2 w-100",
                )
                ui.input_action_button(
                    "show_multiple", "Show Multiple Toasts", class_="mb-2 w-100"
                )
                ui.input_action_button(
                    "show_all_positions", "Test All Positions", class_="mb-2 w-100"
                )

# Store last toast IDs
last_toast_id = reactive.value("")
persistent_toast_id = reactive.value("")


# Show toast from builder
@reactive.effect
@reactive.event(input.show_toast)
def _():
    # Build header if needed
    header = None
    if input.use_header():
        header_icon = None
        if input.header_icon():
            header_icon = icon_svg(input.header_icon())

        header = toast_header(
            title=input.header_title(),
            icon=header_icon,
            status=None,
        )

    # Build body icon if not using header
    body_icon = None
    if not input.use_header() and input.icon_body():
        body_icon = icon_svg(input.icon_body())

    # Build toast
    toast_obj = toast(
        input.body(),
        header=header,
        icon=body_icon,
        type=input.type() if input.type() else None,
        duration=input.duration() if input.duration() > 0 else None,
        position=input.position(),
        closable=input.closable(),
    )

    # Show and store ID
    id = ui.show_toast(toast_obj)
    last_toast_id.set(id)


# Hide last toast
@reactive.effect
@reactive.event(input.hide_toast)
def _():
    if last_toast_id():
        ui.hide_toast(last_toast_id())
        last_toast_id.set("")


# Advanced features
@reactive.effect
@reactive.event(input.show_persistent)
def _():
    id = ui.show_toast(
        toast(
            "This toast won't disappear automatically. Use the 'Hide' button to dismiss it.",
            header="Persistent Toast",
            type="info",
            duration=None,
        )
    )
    persistent_toast_id.set(id)


@reactive.effect
@reactive.event(input.hide_persistent)
def _():
    if persistent_toast_id():
        ui.hide_toast(persistent_toast_id())
        persistent_toast_id.set("")


@reactive.effect
@reactive.event(input.show_long_duration)
def _():
    ui.show_toast(
        toast(
            "This toast will stay visible for 10 seconds.",
            header="Long Duration",
            type="primary",
            duration=10,
        )
    )


@reactive.effect
@reactive.event(input.show_no_close)
def _():
    ui.show_toast(
        toast(
            "This toast has no close button but will auto-hide in 3 seconds.",
            type="secondary",
            closable=False,
            duration=3,
        )
    )


@reactive.effect
@reactive.event(input.show_custom_header)
def _():
    ui.show_toast(
        toast(
            "Your profile has been updated successfully.",
            header=toast_header(
                title="Profile Updated",
                icon=icon_svg("check"),
                status="just now",
            ),
            type="success",
        )
    )


# Interactive toasts
@reactive.effect
@reactive.event(input.show_action_buttons)
def _():
    ui.show_toast(
        toast(
            ui.p("Would you like to save your changes?"),
            ui.div(
                ui.input_action_button(
                    "save_yes", "Save", class_="btn-sm btn-primary me-2"
                ),
                ui.input_action_button(
                    "save_no", "Don't Save", class_="btn-sm btn-secondary"
                ),
                class_="mt-2",
            ),
            id="unsaved_changes_toast",
            header="Unsaved Changes",
            type="warning",
            duration=None,
            closable=False,
        )
    )


@reactive.effect
@reactive.event(input.save_yes)
def _():
    ui.hide_toast("unsaved_changes_toast")
    ui.show_toast(toast("Saved changes", type="success"))


@reactive.effect
@reactive.event(input.save_no)
def _():
    ui.hide_toast("unsaved_changes_toast")
    ui.show_toast(toast("Changes were not saved", type="danger"))


@reactive.effect
@reactive.event(input.show_multiple)
def _():
    ui.show_toast(toast("First notification", type="primary"))
    time.sleep(0.2)
    ui.show_toast(toast("Second notification", type="success"))
    time.sleep(0.2)
    ui.show_toast(toast("Third notification", type="info"))


@reactive.effect
@reactive.event(input.show_all_positions)
def _():
    positions = [
        "top-left",
        "top-center",
        "top-right",
        "middle-left",
        "middle-center",
        "middle-right",
        "bottom-left",
        "bottom-center",
        "bottom-right",
    ]

    types = [
        "primary",
        "success",
        "info",
        "warning",
        "danger",
        "secondary",
        "light",
        "dark",
        "primary",
    ]

    for i, pos in enumerate(positions):
        ui.show_toast(
            toast(
                f"Toast at {pos}",
                type=types[i],
                duration=4,
                position=pos,
            )
        )
