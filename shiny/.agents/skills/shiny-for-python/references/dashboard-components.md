# Composing dashboard cards and controls

## Overview

Use cards as the main analytical unit. A good card has a focused title, one primary
output, and only the controls or explanation needed to interpret that output. Use
value boxes for headline metrics, toolbars for compact card-local controls, and
tooltips or popovers for secondary explanation.

## Contents

- Put local controls in the card header
- Build meaningful value boxes
- Use icons accessibly
- Choose a tooltip or popover
- Keep cards legible
- Quick reference
- Common mistakes

## Put local controls in the card header

Controls that filter the whole page belong in a sidebar. Controls that change one
card's measure, grouping, sort order, or display mode belong in that card header.

```python
from faicons import icon_svg
from shiny import ui
from shinywidgets import output_widget

sales_card = ui.card(
    ui.card_header(
        "Revenue trend",
        ui.toolbar(
            ui.toolbar_input_select(
                "trend_period",
                "Period",
                choices={"week": "Week", "month": "Month"},
                selected="month",
                icon=icon_svg("calendar"),
            ),
            ui.toolbar_input_button(
                "download_trend",
                "Download chart",
                icon=icon_svg("download"),
            ),
            align="right",
            gap="0.5rem",
        ),
    ),
    output_widget("revenue_trend"),
    full_screen=True,
)
```

`toolbar_input_button` hides its label when it has an icon and supplies a tooltip
from that label by default. Always provide a meaningful, non-empty label. For a
toolbar select, dictionary keys are input values and dictionary values are displayed
labels.

Use `ui.toolbar_divider()` to separate groups and `ui.toolbar_spacer()` with
`ui.toolbar(width="100%")` to push groups to opposite sides. Update toolbar controls
with `ui.update_toolbar_input_button()` and `ui.update_toolbar_input_select()`.

## Build meaningful value boxes

A value box should contain a metric name, a formatted value, and context such as the
period, target, or change from a baseline.

```python
ui.value_box(
    "Net revenue",
    ui.output_text("net_revenue"),
    ui.output_ui("net_revenue_context"),
    showcase=icon_svg("dollar-sign"),
    theme="primary",
)
```

- Limit a row to roughly three or four headline metrics.
- Use `ui.layout_column_wrap(..., width="240px", fill=False)` so boxes wrap before
  becoming cramped.
- Format the value in its renderer; do not display a raw float.
- Use green/red only when direction truly means good/bad, and accompany color with
  text or an icon.
- Keep showcase icons semantically related. A tiny sparkline may replace an icon when
  the recent trajectory matters, but it must not duplicate a larger chart below.

## Use icons accessibly

`faicons.icon_svg()` is an optional, convenient icon source. Use a small, consistent
icon vocabulary and avoid decorative icons on every heading.

```python
from faicons import icon_svg

ui.toolbar_input_button(
    "refresh",
    "Refresh data",
    icon=icon_svg("rotate"),
)
```

Prefer components such as `toolbar_input_button` that keep a textual label available
to assistive technology. For a standalone semantic icon, use a useful title and
`a11y="sem"`; decorative icons should stay hidden from assistive technology.

## Choose a tooltip or popover

Use a tooltip for a short label or definition. Use a popover when the explanation
needs several lines, formatting, or a small control. Neither should contain essential
information that is unavailable to keyboard or touch users.

```python
ui.card_header(
    "Conversion rate",
    ui.tooltip(
        icon_svg("circle-info", title="Define conversion rate", a11y="sem"),
        "Completed orders divided by initiated checkouts.",
        placement="left",
    ),
)

ui.popover(
    ui.input_action_button("method_help", "Methodology"),
    ui.h5("Methodology"),
    ui.p("Metrics exclude test accounts and refunded orders."),
    title="How this page is calculated",
)
```

Use stable `id=` values when the server must open, close, or update a tooltip or
popover.

## Keep cards legible

- Put one main chart or table in each card.
- Use a compact toolbar rather than a second row of full-size form inputs.
- Use `full_screen=True` for dense charts, maps, and tables.
- Avoid card headers that wrap into three lines because of too many actions.
- Show a short empty-state message inside the card when filters return no rows.
- Use a footer for source/provenance or update time, not for primary controls.

## Quick reference

| Need | Use |
|---|---|
| Card-local button/select | `ui.toolbar()` with `toolbar_input_*()` |
| Split toolbar groups | `toolbar_spacer()` with `width="100%"` |
| KPI or headline metric | `ui.value_box()` |
| Short definition | `ui.tooltip()` |
| Rich secondary explanation | `ui.popover()` |
| Programmatic toolbar update | `update_toolbar_input_button()` / `update_toolbar_input_select()` |

## Common mistakes

- Putting every display option in the global sidebar.
- Using a bare icon as a button with no accessible name.
- Giving the value box a color unrelated to the metric's meaning.
- Making hover-only content essential to understanding the dashboard.
- Reusing the same toolbar or output ID in multiple cards.
