
# Transient user feedback in Shiny for Python

## Overview

Feedback that appears briefly and then goes away — toasts, dialogs, progress
bars, spinners — is sent from the **server**, almost always from inside a
`@reactive.effect`. These are overlays managed by Shiny: you show them and
Shiny handles rendering and dismissal.

Do NOT fake these with `ui.panel_conditional` + `@render.ui`, do NOT
`print()` status to the console (the user never sees it), and do NOT run a long
loop with no visible indication that the app is working. Use the built-in
overlays below.

## Toast notifications

Non-blocking messages that stack in a corner and auto-dismiss. Call
`ui.notification_show(msg, type=, duration=, id=)`; `type` is one of
`"default"`, `"message"`, `"warning"`, `"error"`. It returns the notification
id. Pass `duration=None` to keep it up until removed, and reuse the same `id`
to update a notification in place.

```python
from shiny import App, Inputs, Outputs, Session, reactive, ui

app_ui = ui.page_fluid(ui.input_action_button("save", "Save"))

def server(input: Inputs, output: Outputs, session: Session):
    @reactive.effect
    @reactive.event(input.save)
    def _():
        id = ui.notification_show("Saving...", duration=None)
        # ...do work...
        ui.notification_remove(id)
        ui.notification_show("Saved!", type="message", duration=3)

app = App(app_ui, server)
```

## Modal dialogs

A blocking dialog for important messages or for collecting input. Build it with
`ui.modal(...)` and display it with `ui.modal_show(...)`. Close it from the
server with `ui.modal_remove()`, or give the user a `ui.modal_button(label)` in
the footer (it dismisses the modal client-side). `easy_close=True` lets the
user dismiss by clicking outside or pressing Escape.

```python
from shiny import App, Inputs, Outputs, Session, reactive, ui

app_ui = ui.page_fluid(ui.input_action_button("show", "Show dialog"))

def server(input: Inputs, output: Outputs, session: Session):
    @reactive.effect
    @reactive.event(input.show)
    def _():
        m = ui.modal(
            "This action cannot be undone.",
            title="Are you sure?",
            easy_close=True,
            footer=ui.modal_button("Cancel"),
        )
        ui.modal_show(m)

app = App(app_ui, server)
```

Inputs placed inside a modal are ordinary Shiny inputs: read them by id after
the user acts, then call `ui.modal_remove()`.

## Progress bars for multi-step work

For a known sequence of steps, use `ui.Progress` as a context manager and call
`p.set(value, message=, detail=)` as you advance. The bar closes automatically
on exit. Use `p.inc(amount)` to advance by a step instead of setting an
absolute value.

```python
import asyncio
from shiny import App, Inputs, Outputs, Session, reactive, render, ui

app_ui = ui.page_fluid(
    ui.input_action_button("go", "Run"),
    ui.output_text("done"),
)

def server(input: Inputs, output: Outputs, session: Session):
    @render.text
    @reactive.event(input.go)
    async def done():
        with ui.Progress(min=1, max=15) as p:
            p.set(message="Working", detail="This may take a while...")
            for i in range(1, 15):
                p.set(i, message="Computing")
                await asyncio.sleep(0.1)
        return "Done!"

app = App(app_ui, server)
```

For a single long-running computation triggered by a button, an
`@ui.input_task_button` with an extended task often fits better (see
`references/extended-tasks.md`); `Progress` is for reporting incremental steps.

## Busy indicators (spinners and pulse)

Busy indicators are the automatic spinners on recalculating outputs and the
pulsing banner shown while the app is busy — they need **no server code**. They
are on by default. Configure them by placing the result of these functions in
the app UI (not in the server):

- `ui.busy_indicators.use(spinners=, pulse=, fade=)` — enable/disable each.
- `ui.busy_indicators.options(spinner_type=, spinner_color=, spinner_size=, ...)`
  — customize appearance.

```python
from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.busy_indicators.use(spinners=True, pulse=False),
    ui.busy_indicators.options(spinner_type="bars3", spinner_color="#0d6efd"),
    ui.output_plot("plot"),
)
```

## Quick reference

| Need | Use |
|---|---|
| Brief, non-blocking message | `ui.notification_show(msg, type=, duration=)` |
| Remove/update a notification | `ui.notification_remove(id)` (reuse `id` to replace) |
| Blocking dialog / collect input | `ui.modal(...)` + `ui.modal_show(...)` |
| Close a modal from server / user | `ui.modal_remove()` / `ui.modal_button(label)` |
| Report progress over known steps | `with ui.Progress() as p: p.set(value, message=)` |
| Spinner/pulse on busy outputs | `ui.busy_indicators.use(...)` / `.options(...)` in UI |

## Common mistakes

- Calling `ui.notification_show` / `ui.modal_show` / `ui.Progress` at server top
  level or in the UI -> they need an active session and a reactive trigger.
  Call them inside a `@reactive.effect` (usually with `@reactive.event`).
- Expecting `ui.notification_remove` to work without an id -> capture the id
  returned by `notification_show` and pass it back.
- Putting `ui.busy_indicators.use/options` in the server function -> they are UI
  elements; add them to the `app_ui`.
- `duration` is in **seconds**, not milliseconds; `duration=None` means "stay
  until removed", not "no notification".
- Building a fake popup with `panel_conditional` + `@render.ui` -> use `ui.modal`
  for dialogs and `ui.notification_show` for toasts.
- Running a long loop with only `print()` for status -> the user sees nothing;
  use `ui.Progress` or a notification.
