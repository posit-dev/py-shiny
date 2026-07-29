"""
Session Destroy Demo
====================
Demonstrates `session.destroy()` cleaning up reactive objects when dynamic UI
is removed. Each panel creates effects, calcs, and inputs inside a module.
When "Remove this panel" is clicked, `session.destroy()` destroys all
server-side reactive state for that module.

How to use:
- Click "Create Panel" to add panels. Each panel has an auto-incrementing
  effect, a dynamic text input, and a calc derived from that input.
- Click "Remove this panel" — the panel is removed and all its reactive
  state is cleaned up via `session.destroy()`.
- Watch the "Reactive State Monitor" in the sidebar: removed panels show
  as cleaned up with their final state frozen.
"""

from collections.abc import Callable
from typing import Any

from shiny import App, Inputs, Outputs, Session, module, reactive, render, ui
from shiny.types import SilentException


# ---------------------------------------------------------------------------
# Module: one panel of dynamic content
# ---------------------------------------------------------------------------
@module.ui
def panel_ui():
    return ui.card(
        ui.card_header(
            ui.output_text("panel_title", inline=True),
            ui.input_action_button(
                "remove", "Remove this panel", class_="btn-danger btn-sm float-end"
            ),
        ),
        ui.input_checkbox("show_dynamic", "Show dynamic UI", value=True),
        ui.output_ui("dynamic_area"),
        ui.card_footer(ui.output_text_verbatim("local_status")),
    )


@module.server
def panel_server(
    input: Inputs,
    output: Outputs,
    session: Session,
    panel_num: int,
    tracker: reactive.Value[dict[str, Any]],
    on_remove: Callable[[], None],
):
    effect_counter = reactive.value(0)

    @render.text
    def panel_title():
        return f"Panel {panel_num}"

    # Effect: auto-increments a counter every second.
    # Destroyed by session.destroy() when the panel is removed.
    @reactive.effect
    def auto_increment():
        reactive.invalidate_later(1)
        with reactive.isolate():
            new_count = effect_counter.get() + 1
            effect_counter.set(new_count)

    # Calc: derives a value from the dynamic input.
    # Destroyed by session.destroy() when the panel is removed.
    @reactive.calc
    def derived_message():
        try:
            val = input.dynamic_txt()
            return f"Derived: '{val}'"
        except SilentException:
            return "(input not yet available)"

    @render.ui
    def dynamic_area():
        if not input.show_dynamic():
            return ui.div(
                ui.p(
                    "Dynamic UI is hidden. The effect continues to fire "
                    "since the module is still active.",
                    class_="text-muted fst-italic",
                ),
            )
        return ui.TagList(
            ui.input_text(
                "dynamic_txt",
                "Type something:",
                value=f"hello from panel {panel_num}",
                width="100%",
            ),
            ui.p(
                ui.strong("Calc output: "),
                ui.output_text("calc_display", inline=True),
            ),
        )

    @render.text
    def calc_display():
        return derived_message()

    @render.text
    def local_status():
        return f"Effect has fired {effect_counter.get()} times"

    # Update the shared tracker so the global monitor can see our state.
    # This effect is destroyed by session.destroy() when the panel is removed.
    @reactive.effect
    def update_tracker():
        count = effect_counter.get()
        calc_val = derived_message()

        try:
            input_val = input.dynamic_txt()
        except SilentException:
            input_val = "(never set)"

        with reactive.isolate():
            t = tracker.get().copy()
            t[f"panel_{panel_num}"] = {
                "effect_count": count,
                "input_value": repr(input_val),
                "calc_value": calc_val,
                "removed": t.get(f"panel_{panel_num}", {}).get("removed", False),
            }
            tracker.set(t)

    # Remove handler
    @reactive.effect
    @reactive.event(input.remove)
    async def handle_remove():
        # Mark as removed in tracker BEFORE removing the UI
        t = tracker.get().copy()
        key = f"panel_{panel_num}"
        if key in t:
            t[key]["removed"] = True
            tracker.set(t)

        # Remove the DOM element
        ui.remove_ui(selector=f"div#{session.ns('panel_ui_container')}")
        # Clean up all server-side reactive objects for this module
        await session.destroy()
        on_remove()


# ---------------------------------------------------------------------------
# Shiny app
# ---------------------------------------------------------------------------
app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_action_button(
            "create_panel", "Create Panel", class_="btn-primary w-100 mb-3"
        ),
        ui.hr(),
        ui.h5("Reactive State Monitor"),
        ui.p(
            "Server-side state for all panels. Removed panels show "
            "their final state, frozen after destroy.",
            class_="text-muted small",
        ),
        ui.output_ui("status_panel"),
        width=400,
        open="always",
    ),
    ui.div(id="panel_container"),
    title="Session Destroy Demo",
    fillable=False,
)


def server(input: Inputs, output: Outputs, session: Session):
    panel_counter = reactive.value(0)
    tracker: reactive.Value[dict[str, Any]] = reactive.value({})
    active_panels: reactive.Value[set[str]] = reactive.value(set())

    @reactive.effect
    @reactive.event(input.create_panel)
    def _():
        n = panel_counter.get() + 1
        panel_counter.set(n)
        panel_id = f"panel_{n}"

        # Track active panels
        panels = active_panels.get().copy()
        panels.add(panel_id)
        active_panels.set(panels)

        # Insert the module UI
        ui.insert_ui(
            selector="#panel_container",
            where="beforeEnd",
            ui=ui.div(
                panel_ui(panel_id),
                id=f"{panel_id}-panel_ui_container",
                class_="mb-3",
            ),
        )

        # Start the module server
        def make_remove_callback(pid: str):
            def on_remove():
                panels = active_panels.get().copy()
                panels.discard(pid)
                active_panels.set(panels)

            return on_remove

        panel_server(
            panel_id,
            panel_num=n,
            tracker=tracker,
            on_remove=make_remove_callback(panel_id),
        )

    # -----------------------------------------------------------------------
    # Global status monitor
    # -----------------------------------------------------------------------
    @render.ui
    def status_panel():
        t = tracker.get()

        if not t:
            return ui.p("No panels created yet.", class_="text-muted fst-italic")

        items: list[ui.Tag] = []
        for panel_key in sorted(t.keys()):
            info = t[panel_key]
            removed = info.get("removed", False)

            border_class = (
                "border-success bg-success-subtle" if removed else "border-info"
            )
            label = " [DESTROYED]" if removed else ""

            items.append(
                ui.div(
                    ui.strong(f"{panel_key}{label}"),
                    ui.tags.table(
                        ui.tags.tr(
                            ui.tags.td("Effect fires:", class_="pe-2 small text-muted"),
                            ui.tags.td(
                                str(info["effect_count"]),
                                class_="small fw-bold font-monospace",
                            ),
                        ),
                        ui.tags.tr(
                            ui.tags.td("Input value:", class_="pe-2 small text-muted"),
                            ui.tags.td(
                                info["input_value"],
                                class_="small font-monospace",
                            ),
                        ),
                        ui.tags.tr(
                            ui.tags.td("Calc value:", class_="pe-2 small text-muted"),
                            ui.tags.td(
                                info["calc_value"],
                                class_="small font-monospace",
                            ),
                        ),
                        class_="mb-0",
                    ),
                    class_=f"mb-2 p-2 border rounded {border_class}",
                )
            )

        return ui.TagList(*items)


app = App(app_ui, server)
