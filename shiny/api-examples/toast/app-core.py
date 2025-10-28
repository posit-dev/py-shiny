import time

from faicons import icon_svg

from shiny import App, Inputs, Outputs, Session, reactive, render, ui

app_ui = ui.page_fillable(
    ui.h2("Toast Notifications Demo", class_="p-3 border-bottom mb-0"),
    ui.input_dark_mode(class_="position-absolute top-0 end-0 p-3"),
    ui.layout_column_wrap(
        1 / 2,
        # Toast Builder Card
        ui.card(
            ui.card_header("Toast Builder"),
            ui.card_body(
                # Body content
                ui.input_text_area(
                    "body",
                    "Body Content",
                    value="This is a toast notification!",
                    rows=3,
                    width="100%",
                ),
                ui.layout_columns(
                    ui.div(
                        # Type
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
                        ),
                        # Position
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
                        ),
                        # Duration
                        ui.input_slider(
                            "duration",
                            "Duration (seconds, 0 = disabled)",
                            min=0,
                            max=25,
                            value=5,
                            step=1,
                            ticks=False,
                        ),
                        # Close button
                        ui.input_switch("closable", "Show Close Button", value=True),
                        ui.input_text(
                            "custom_id",
                            "Toast ID",
                            placeholder="Automatically generated",
                        ),
                    ),
                    ui.div(
                        # Header options
                        ui.input_switch("use_header", "Include Header", value=False),
                        ui.panel_conditional(
                            "input.use_header",
                            ui.input_text(
                                "header_title", "Header Title", value="Notification"
                            ),
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
                            ),
                            ui.input_text(
                                "header_status",
                                "Custom Status Text",
                                placeholder="'Just now', '2 mins ago'",
                            ),
                        ),
                        ui.panel_conditional(
                            "!input.use_header",
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
                            ),
                        ),
                    ),
                ),
            ),
            ui.card_footer(
                ui.input_action_button(
                    "show_toast", "Show Toast", class_="btn-primary"
                ),
                ui.input_action_button(
                    "hide_toast", "Hide Last Toast", class_="btn-secondary"
                ),
                class_="hstack gap-2 justify-content-end",
            ),
        ),
        ui.layout_column_wrap(
            1,
            # Advanced Features
            ui.card(
                ui.card_header("Advanced Features"),
                ui.card_body(
                    ui.input_action_button(
                        "show_persistent",
                        "Show Persistent Toast",
                        class_="mb-2 w-100",
                    ),
                    ui.input_action_button(
                        "hide_persistent",
                        "Hide Persistent Toast",
                        class_="mb-2 w-100",
                    ),
                    ui.input_action_button(
                        "show_long_duration",
                        "Long Duration (10s)",
                        class_="mb-2 w-100",
                    ),
                    ui.input_action_button(
                        "show_no_close", "No Close Button", class_="mb-2 w-100"
                    ),
                    ui.input_action_button(
                        "show_custom_header",
                        "Custom Header with Icon & Status",
                        class_="mb-2 w-100",
                    ),
                ),
            ),
            # Interactive Toasts
            ui.card(
                ui.card_header("Interactive Toasts"),
                ui.card_body(
                    ui.input_action_button(
                        "show_action_buttons",
                        "Toast with Action Buttons",
                        class_="mb-2 w-100",
                    ),
                    ui.input_action_button(
                        "show_multiple", "Show Multiple Toasts", class_="mb-2 w-100"
                    ),
                    ui.input_action_button(
                        "show_all_positions", "Test All Positions", class_="mb-2 w-100"
                    ),
                    ui.input_action_button(
                        "show_dynamic_content",
                        "Toast with Dynamic Content",
                        class_="mb-2 w-100",
                    ),
                ),
            ),
        ),
        class_="bslib-page-dashboard",
        style="background: var(--bslib-dashboard-main-bg); padding: 15px; gap: 15px",
    ),
    title="Toast Notifications Demo",
    padding=0,
    gap=0,
)


def server(input: Inputs, output: Outputs, session: Session):
    # Store last toast IDs
    last_toast_id = reactive.value("")
    persistent_toast_id = reactive.value("")
    inserted_time = reactive.value(None)

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

            header = ui.toast_header(
                title=input.header_title(),
                icon=header_icon,
                status=input.header_status() if input.header_status() else None,
            )

        # Build body content
        body_content = []
        if not input.use_header() and input.icon_body():
            body_content.append(icon_svg(input.icon_body(), class_="me-2"))
        body_content.append(input.body())

        # Build toast
        toast_obj = ui.toast(
            *body_content,
            header=header,
            id=input.custom_id() if input.custom_id() else None,
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
            ui.toast(
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
            ui.toast(
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
            ui.toast(
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
            ui.toast(
                "Your profile has been updated successfully.",
                header=ui.toast_header(
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
            ui.toast(
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
        ui.show_toast(ui.toast("Saved changes", type="success"))

    @reactive.effect
    @reactive.event(input.save_no)
    def _():
        ui.hide_toast("unsaved_changes_toast")
        ui.show_toast(ui.toast("Changes were not saved", type="danger"))

    @reactive.effect
    @reactive.event(input.show_multiple)
    def _():
        ui.show_toast(ui.toast("First notification", type="primary"))
        time.sleep(0.2)
        ui.show_toast(ui.toast("Second notification", type="success"))
        time.sleep(0.2)
        ui.show_toast(ui.toast("Third notification", type="info"))

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
                ui.toast(
                    f"Toast at {pos}",
                    type=types[i],
                    duration=4,
                    position=pos,
                )
            )

    # Dynamic content toast
    @reactive.effect
    @reactive.event(input.show_dynamic_content)
    def _():
        ui.show_toast(
            ui.toast(
                ui.div(
                    ui.p("Current time:", ui.strong(ui.output_text("toast_time"))),
                    ui.output_plot("toast_plot", height="200px"),
                    ui.input_slider(
                        "toast_bins",
                        "Number of bins:",
                        min=5,
                        max=50,
                        value=30,
                        width="100%",
                    ),
                ),
                id="dynamic_content_toast",
                header=ui.toast_header(
                    title="Dynamic Toast",
                    status=ui.output_text("toast_status"),
                ),
                type="light",
                duration=None,
            )
        )
        inserted_time.set(time.time())

    @render.text
    def toast_time():
        reactive.invalidate_later(1)
        return time.strftime("%H:%M:%S")

    @render.text
    def toast_status():
        if inserted_time() is None:
            return ""

        reactive.invalidate_later(1)
        elapsed = time.time() - inserted_time()
        if elapsed < 60:
            return f"{int(elapsed)}s ago"
        else:
            return f"{int(elapsed / 60)}m ago"

    @render.plot
    def toast_plot():
        import matplotlib.pyplot as plt
        import numpy as np

        # Generate sample data (simulating faithful dataset)
        np.random.seed(42)
        eruptions = np.concatenate(
            [np.random.normal(2, 0.5, 150), np.random.normal(4.5, 0.5, 150)]
        )

        fig, ax = plt.subplots(figsize=(6, 3))
        ax.hist(
            eruptions,
            bins=input.toast_bins() if input.toast_bins() else 30,
            color="#444",
            edgecolor="none",
        )
        ax.set_title("Eruption Times")
        ax.set_xlabel("")
        ax.set_ylabel("")
        ax.set_xticks([])
        ax.set_yticks([])
        fig.patch.set_alpha(0)
        ax.patch.set_alpha(0)
        plt.tight_layout()
        return fig


app = App(app_ui, server)
