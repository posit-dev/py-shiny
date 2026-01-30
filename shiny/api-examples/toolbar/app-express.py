from shiny.express import input, render, ui

ui.page_opts(title="Toolbar Examples - Express", fillable=True)

ui.h2("Toolbar Examples (Shiny Express)")

with ui.layout_columns(col_widths=[6, 6]):
    # Example 1: Document Editor
    with ui.card():
        with ui.card_header():
            "Document Editor"
            with ui.toolbar(align="right", gap="0.25rem"):
                ui.toolbar_input_button("save_doc", label="Save", icon=ui.HTML("💾"))
                ui.toolbar_input_button("share", label="Share", icon=ui.HTML("📤"))
                ui.toolbar_divider()
                ui.toolbar_input_button("info", label="Info", icon=ui.HTML("ℹ️"))

        @render.text
        def doc_actions():
            actions = []
            if input.save_doc():
                actions.append(f"Save: {input.save_doc()}")
            if input.share():
                actions.append(f"Share: {input.share()}")
            if input.info():
                actions.append(f"Info: {input.info()}")
            return " | ".join(actions) if actions else "No actions yet"

    # Example 2: Filters
    with ui.card():
        with ui.card_header():
            "Data Filters"
            with ui.toolbar(align="right"):
                ui.toolbar_input_select(
                    "status_filter",
                    label="Status",
                    choices=["All", "Active", "Inactive"],
                    icon=ui.HTML("🔍"),
                )
                ui.toolbar_input_select(
                    "category",
                    label="Category",
                    choices={
                        "tech": "Technology",
                        "health": "Health",
                        "edu": "Education",
                    },
                    show_label=True,
                )

        @render.text
        def filter_status():
            return f"Status: {input.status_filter()} | Category: {input.category()}"


with ui.layout_columns(col_widths=12):
    # Example 3: Full-width card with left-aligned toolbar
    with ui.card():
        with ui.card_header():
            "Task Manager"
            with ui.toolbar(align="left", gap="0.5rem"):
                ui.toolbar_input_button(
                    "add_task",
                    label="Add Task",
                    icon=ui.HTML("➕"),
                    show_label=True,
                    border=True,
                )
                ui.toolbar_divider()
                ui.toolbar_input_select(
                    "task_view",
                    label="View",
                    choices=["List", "Board", "Calendar"],
                )
                ui.toolbar_input_select(
                    "task_filter",
                    label="Filter",
                    choices=["All Tasks", "My Tasks", "Completed"],
                )

        @render.text
        def task_info():
            add_count = input.add_task() if input.add_task() else 0
            return (
                f"Add Task clicked: {add_count} times\n"
                f"View: {input.task_view()}\n"
                f"Filter: {input.task_filter()}"
            )
