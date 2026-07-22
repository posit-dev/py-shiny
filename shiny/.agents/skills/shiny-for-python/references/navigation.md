---
name: navigation
description: Covers Shiny for Python (py-shiny) multi-panel navigation - the navset_*() family (tab, pill, underline, card variants, pill_list, bar, hidden), nav_panel/nav_menu/nav_control/nav_spacer children, page_navbar() for a top-level navbar app, reading the active panel via the navset id input, switching it with update_navset(), and adding/removing panels at runtime with insert_nav_panel/remove_nav_panel/update_nav_panel. Use when organizing an app into tabs, pills, or a navbar with multiple pages, reading or switching the active tab from the server, adding or removing tabs at runtime, or when tempted to build tab buttons with input_action_button + conditional_panel to fake tabbed navigation.
---

# Navigation in Shiny for Python

## Overview

Group content into switchable panels with a `navset_*()` container holding
`nav_panel()` children. Each `nav_panel(title, *content, value=)` is one panel;
the container renders the tab strip and shows one panel at a time.

Do NOT fake tabs with `input_action_button` + `conditional_panel` or by
toggling `@render.ui` — a navset gives you the tab strip, active styling,
keyboard/ARIA behavior, and a server-readable selection for free. To read or
change which panel is active, give the container an `id=` (see below); don't
track the selection in a separate `reactive.value`.

This documents the Core form. Express mode uses `with ui.nav_panel(...):`
context managers — see the `express` skill.

## Choose a container

Every `navset_*()` takes the same core args: `*args` (nav items), `id=`,
`selected=`, `header=`, `footer=`. Pick by appearance:

```python
from shiny import ui

ui.navset_tab(                      # classic bordered tabs
    ui.nav_panel("Plot", "plot content"),
    ui.nav_panel("Table", "table content"),
    id="which",                     # optional: exposes input.which()
)
```

Swap `navset_tab` for `navset_pill` (rounded buttons), `navset_underline`
(underlined links), or the `navset_card_*` variants to wrap the panels in a
`card` with the tabs in its header. `navset_pill_list` renders a vertical list
beside the content. `navset_hidden` shows no tab strip at all — you drive it
entirely from the server (pair it with `update_navset`).

## A top-level navbar app: `page_navbar`

`page_navbar()` is a full page whose top-level nav items become navbar pages.
Its `*args` are nav items directly (no inner `navset_*`):

```python
from shiny import App, ui

app_ui = ui.page_navbar(
    ui.nav_panel("Home", "welcome"),
    ui.nav_panel("Analysis", ui.output_plot("p")),
    ui.nav_menu(                     # dropdown of nav items
        "More",
        ui.nav_panel("About", "about page"),
        "----",                      # a string of hyphens is a divider
        ui.nav_control(ui.a("Docs", href="https://shiny.posit.co")),
    ),
    title="My App",
    id="page",                       # input.page() == active panel value
    sidebar=ui.sidebar("Shared across pages"),
)
```

- `nav_menu(title, *items)` — a dropdown; string args become section headers,
  `"---"` becomes a divider.
- `nav_control(...)` — arbitrary UI (e.g. a link) in the nav strip.
- `nav_spacer()` — pushes later items to the right.
- `sidebar=` puts one sidebar on every page. Style the bar with
  `navbar_options=ui.navbar_options(position=..., bg=..., theme=...)`.

To build a navbar *inside* a larger page instead of as the whole page, use
`ui.navset_bar(..., title=...)`.

## Read the active panel

Give the container an `id`. That `id` becomes an input holding the `value` of
the selected panel (its `title` if no `value=` was set):

```python
@render.text
def current():
    return f"You are on: {input.which()}"   # matches the navset id=
```

## Switch panels from the server: `update_navset`

```python
from shiny import reactive, ui

@reactive.effect
@reactive.event(input.go_to_table)
def _():
    ui.update_navset("which", selected="Table")   # id, then panel value
```

## Add / remove / show / hide panels at runtime

Target panels by their `value`. Insert relative to an existing `target`:

```python
@reactive.effect
@reactive.event(input.add)
def _():
    ui.insert_nav_panel(
        "which",                                   # navset id
        ui.nav_panel("New", "fresh content", value="new"),
        target="Table", position="before", select=True,
    )

@reactive.effect
@reactive.event(input.drop)
def _():
    ui.remove_nav_panel("which", target="new")
```

`ui.update_nav_panel("which", target="new", method="hide")` (or `"show"`)
toggles visibility without removing the panel. Showing a hidden panel does not
select it — follow with `update_navset("which", selected="new")` if needed.

## Quick reference

| Container | Looks like |
|---|---|
| `navset_tab` | Classic bordered tabs |
| `navset_pill` | Rounded pill buttons |
| `navset_underline` | Underlined active link |
| `navset_card_tab` | Tabs in a card header |
| `navset_card_pill` | Pills in a card header |
| `navset_card_underline` | Underlined links in a card header |
| `navset_pill_list` | Vertical pill list beside content |
| `navset_bar` | Bootstrap navbar (inside a page) |
| `navset_hidden` | No tab strip; server-driven only |
| `page_navbar` | Full page whose top-level items are navbar pages |

| Task | Call |
|---|---|
| Read active panel | `input.<navset_id>()` |
| Switch panel | `ui.update_navset(id, selected=value)` |
| Add panel | `ui.insert_nav_panel(id, nav_panel, target=, position=, select=)` |
| Remove panel | `ui.remove_nav_panel(id, target=value)` |
| Show/hide panel | `ui.update_nav_panel(id, target=value, method="show"/"hide")` |

## Common mistakes

- Reading the active tab and finding no input -> the navset needs an `id=`.
  Without it there is no `input.<id>()`; the selection is not exposed.
- `input.<id>()` / `update_navset` / `insert_nav_panel` use the panel's
  `value`, not its `title`. If you set `value="table"`, then `input.id()` is
  `"table"` and `selected="Table"` will not match. When `value=` is omitted it
  defaults to `str(title)`.
- Passing `nav_panel` items straight into `page_fluid`/`page_sidebar` -> nav
  items only render inside a `navset_*()` (or `page_navbar`); otherwise they
  raise "must appear within navset_*() container".
- Building tab buttons with `input_action_button` + `conditional_panel` -> use
  a `navset_*()` with an `id` instead; you get styling, ARIA, and the selection
  input for free.
- Nesting a `navset_bar` as a whole page -> use `page_navbar` for a top-level
  navbar; `navset_bar` is for a navbar embedded in another page.
