from shiny import App, reactive, render, ui

app_ui = ui.page_fillable(
    ui.h2("Toolbar Examples"),
    ui.layout_columns(
        # Example 1: Document Editor with toolbar buttons
        ui.card(
            ui.card_header(
                "Document Editor",
                ui.toolbar(
                    ui.toolbar_input_button(
                        "undo", label="Undo", icon=ui.HTML("↶")
                    ),
                    ui.toolbar_input_button(
                        "redo", label="Redo", icon=ui.HTML("↷")
                    ),
                    ui.toolbar_divider(),
                    ui.toolbar_input_button(
                        "save", label="Save", icon=ui.HTML("💾")
                    ),
                    ui.toolbar_input_button(
                        "settings",
                        label="Settings",
                        icon=ui.HTML("⚙️"),
                        tooltip="Open settings",
                    ),
                    align="right",
                    gap="0.25rem",
                ),
            ),
            ui.card_body(
                ui.p("Edit your document here..."),
                ui.output_text_verbatim("editor_actions"),
            ),
        ),
        # Example 2: Data Table with filtering toolbar
        ui.card(
            ui.card_header(
                "Data Table",
                ui.toolbar(
                    ui.toolbar_input_select(
                        "filter",
                        label="Filter",
                        choices=["All", "Active", "Completed", "Archived"],
                        icon=ui.HTML("🔍"),
                    ),
                    ui.toolbar_input_select(
                        "sort",
                        label="Sort",
                        choices={
                            "name_asc": "Name (A-Z)",
                            "name_desc": "Name (Z-A)",
                            "date_asc": "Date (Oldest)",
                            "date_desc": "Date (Newest)",
                        },
                        selected="date_desc",
                        show_label=True,
                    ),
                    ui.toolbar_divider(),
                    ui.toolbar_input_button(
                        "refresh", label="Refresh", icon=ui.HTML("🔄")
                    ),
                    align="right",
                    gap="0.5rem",
                ),
            ),
            ui.card_body(
                ui.output_text_verbatim("table_status"),
            ),
        ),
        # Example 3: Media Player controls
        ui.card(
            ui.card_header(
                "Media Player",
                ui.toolbar(
                    ui.toolbar_input_button(
                        "play",
                        label="Play",
                        icon=ui.HTML("▶️"),
                        border=True,
                    ),
                    ui.toolbar_input_button(
                        "pause", label="Pause", icon=ui.HTML("⏸")
                    ),
                    ui.toolbar_input_button(
                        "stop", label="Stop", icon=ui.HTML("⏹")
                    ),
                    ui.toolbar_divider(),
                    ui.toolbar_input_select(
                        "speed",
                        label="Speed",
                        choices=["0.5x", "1x", "1.5x", "2x"],
                        selected="1x",
                    ),
                    align="right",
                    gap="0.25rem",
                ),
            ),
            ui.card_body(
                ui.output_text_verbatim("media_status"),
            ),
        ),
        # Example 4: Dynamic updates
        ui.card(
            ui.card_header(
                "Dynamic Toolbar",
                ui.toolbar(
                    ui.toolbar_input_button(
                        "toggle_edit",
                        label="Edit Mode",
                        icon=ui.HTML("✏️"),
                    ),
                    ui.toolbar_input_select(
                        "view",
                        label="View",
                        choices=["List", "Grid", "Table"],
                    ),
                    align="right",
                ),
            ),
            ui.card_body(
                ui.output_text_verbatim("dynamic_status"),
                ui.p(
                    ui.em("Click Edit Mode to toggle between edit and view modes")
                ),
            ),
        ),
        col_widths=[6, 6, 6, 6],
    ),
)


def server(input, output, session):
    # Example 1: Document Editor
    @output
    @render.text
    def editor_actions():
        actions = []
        if input.undo():
            actions.append(f"Undo clicked: {input.undo()} times")
        if input.redo():
            actions.append(f"Redo clicked: {input.redo()} times")
        if input.save():
            actions.append(f"Save clicked: {input.save()} times")
        if input.settings():
            actions.append(f"Settings clicked: {input.settings()} times")
        return "\n".join(actions) if actions else "No actions yet"

    # Example 2: Data Table
    @output
    @render.text
    def table_status():
        refresh_count = input.refresh() if input.refresh() else 0
        return (
            f"Filter: {input.filter()}\n"
            f"Sort: {input.sort()}\n"
            f"Refreshed: {refresh_count} times"
        )

    # Example 3: Media Player
    @output
    @render.text
    def media_status():
        status_lines = []
        if input.play():
            status_lines.append(f"▶️  Playing (clicked {input.play()} times)")
        if input.pause():
            status_lines.append(f"⏸  Paused (clicked {input.pause()} times)")
        if input.stop():
            status_lines.append(f"⏹  Stopped (clicked {input.stop()} times)")
        status_lines.append(f"Speed: {input.speed()}")
        return "\n".join(status_lines)

    # Example 4: Dynamic updates
    edit_mode = reactive.value(False)

    @output
    @render.text
    def dynamic_status():
        mode = "Edit Mode" if edit_mode() else "View Mode"
        return f"Current Mode: {mode}\nView: {input.view()}\nToggle clicks: {input.toggle_edit()}"

    @reactive.effect
    @reactive.event(input.toggle_edit)
    def _():
        # Toggle edit mode
        edit_mode.set(not edit_mode())

        if edit_mode():
            # Switch to edit mode
            ui.update_toolbar_input_button(
                "toggle_edit",
                label="View Mode",
                icon=ui.HTML("👁️"),
            )
        else:
            # Switch to view mode
            ui.update_toolbar_input_button(
                "toggle_edit",
                label="Edit Mode",
                icon=ui.HTML("✏️"),
            )


app = App(app_ui, server)
