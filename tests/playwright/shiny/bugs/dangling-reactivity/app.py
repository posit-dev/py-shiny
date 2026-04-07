"""
Dangling Reactivity Demo
=========================
Demonstrates three types of "dangling" reactive state that persist after dynamic
UI is removed:

1. **Dangling effects** — `reactive.effect` created for dynamic UI keeps firing
   even after the UI is removed from the DOM.
2. **Dangling calcs** — `reactive.calc` persists in memory with stale values.
3. **Dangling input values** — `input.xxx()` still returns the last value for
   inputs that no longer exist in the DOM.

How to use:
- Click "Create Panel" to add panels. Each panel has an auto-incrementing
  effect, a dynamic text input, and a calc derived from that input.
- Toggle "Show dynamic UI" off — the effect keeps firing, input values persist.
- Click "Remove this panel" — same thing, but now the whole panel is gone.
- Watch the "Reactive State Monitor" in the sidebar: it shows server-side state
  that should have been cleaned up but wasn't.
"""

from shiny import App, module, reactive, render, ui
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
def panel_server(input, output, session, panel_num, tracker, on_remove):
    effect_counter = reactive.value(0)

    @render.text
    def panel_title():
        return f"Panel {panel_num}"

    # -----------------------------------------------------------------------
    # DANGLING EFFECT: This reactive.effect uses invalidate_later to
    # auto-increment a counter every second. When the panel is removed from
    # the DOM, this effect is NOT destroyed — it keeps firing indefinitely.
    # -----------------------------------------------------------------------
    @reactive.effect
    def auto_increment():
        reactive.invalidate_later(1)
        with reactive.isolate():
            new_count = effect_counter.get() + 1
            effect_counter.set(new_count)

    # -----------------------------------------------------------------------
    # DANGLING CALC: This reactive.calc derives a value from the dynamic
    # input. After the input is removed from the DOM, the calc still holds
    # its last computed value and remains in the reactive graph.
    # reactive.calc has NO destroy() method at all.
    # -----------------------------------------------------------------------
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
                    "Dynamic UI is hidden, but check the monitor — the effect "
                    "is still firing and the input value persists!",
                    class_="text-warning fst-italic",
                ),
            )
        return ui.TagList(
            ui.input_text(
                "dynamic_txt",
                "Type something (this input value will dangle):",
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

    # -----------------------------------------------------------------------
    # Update the shared tracker so the global monitor can see our state.
    # This effect ALSO dangles after removal — it keeps updating the tracker.
    # -----------------------------------------------------------------------
    @reactive.effect
    def update_tracker():
        # Read reactive dependencies first (these trigger re-execution)
        count = effect_counter.get()
        calc_val = derived_message()

        # Read the dynamic input value — this demonstrates DANGLING INPUTS:
        # even after the input is removed from the DOM, this still returns
        # the last value the input had.
        try:
            input_val = input.dynamic_txt()
        except SilentException:
            input_val = "(never set)"

        # Use isolate to read tracker without creating a dependency on it
        # (otherwise we'd have an infinite loop: read tracker -> set tracker -> invalidate)
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
    def handle_remove():
        # Mark as removed in tracker BEFORE removing the UI
        t = tracker.get().copy()
        key = f"panel_{panel_num}"
        if key in t:
            t[key]["removed"] = True
            tracker.set(t)

        # Remove the DOM element
        ui.remove_ui(selector=f"div#{session.ns('panel_ui_container')}")
        # Clean up all server-side reactive objects for this module
        session.teardown()
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
            "Server-side state for ALL panels, including removed ones. "
            "Entries that keep updating after removal prove dangling reactivity.",
            class_="text-muted small",
        ),
        ui.output_ui("status_panel"),
        width=400,
        open="always",
    ),
    ui.div(id="panel_container"),
    title="Dangling Reactivity Demo",
    fillable=False,
)


def server(input, output, session):
    panel_counter = reactive.value(0)
    tracker = reactive.value({})
    active_panels = reactive.value(set())

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

        # Start the module server — its effects will dangle after removal
        def make_remove_callback(pid):
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

        items = []
        for panel_key in sorted(t.keys()):
            info = t[panel_key]
            removed = info.get("removed", False)

            border_class = (
                "border-danger bg-danger-subtle" if removed else "border-info"
            )
            label = " [REMOVED]" if removed else ""
            still_active = (
                " — STILL UPDATING!" if removed and info["effect_count"] > 0 else ""
            )

            items.append(
                ui.div(
                    ui.strong(f"{panel_key}{label}"),
                    ui.span(still_active, class_="text-danger fw-bold"),
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
