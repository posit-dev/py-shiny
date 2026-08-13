# Designing polished analytical dashboards

## Overview

Treat a dashboard as a decision surface, not a gallery of widgets. Start from the
questions a user must answer, create one shared reactive data pipeline, and arrange
the results from summary to explanation to detail. Use Shiny's layout and theme
primitives first; add small CSS rules only when the component APIs cannot express the
design.

Read the topic references for exact APIs. This guide supplies the cross-cutting
workflow and the quality bar.

## Contents

- Plan the analytical story
- Build one reactive data pipeline
- Establish a visual system
- Compose for hierarchy and responsiveness
- Design useful states
- Verify function and appearance
- Common mistakes

## Plan the analytical story

Before writing UI code, identify:

1. The audience and the decision they need to make.
2. Three to five headline metrics, including their period or comparison context.
3. The few global filters that should affect most of the page.
4. The charts that explain movement or differences in those metrics.
5. The table or drill-down that lets users inspect individual records.

Do not make every available column a filter or every metric a card. Default to this
reading order for a conventional dashboard:

1. Page title and a short scope/status line.
2. A row of three or four value boxes.
3. One primary chart, optionally paired with one supporting chart or map.
4. A detailed table at the bottom.

Use `ui.page_sidebar()` for one workflow with shared filters. Use
`ui.page_navbar()` only when sections support meaningfully different tasks. See
`references/layouts.md` and `references/navigation.md` for the APIs.

## Build one reactive data pipeline

Load static local data once, outside reactive functions. Normalize column types and
derive stable choice lists once. Put user-driven filtering in one
`@reactive.calc`, then have KPIs, charts, maps, and tables read that calculation.

```python
from pathlib import Path

import pandas as pd
from shiny import reactive

DATA = pd.read_csv(Path(__file__).parent / "sales.csv")
DATA["revenue"] = pd.to_numeric(DATA["revenue"], errors="coerce")

@reactive.calc
def filtered_sales():
    frame = DATA
    if input.region():
        frame = frame[frame["region"].isin(input.region())]
    return frame
```

Do not repeat the filtering expression in every renderer. Repeated logic drifts and
can make two cards disagree about the same selection.

## Establish a visual system

- Choose one `ui.Theme` or `_brand.yml` source before styling individual cards.
- Use one primary accent plus neutrals. Reserve success, warning, and danger colors
  for actual meaning rather than decoration.
- Reuse a short categorical color mapping across charts and maps so a category does
  not change color between views.
- Prefer sentence-case titles that describe the measure, such as "Revenue by
  region", rather than generic titles such as "Chart 1".
- Put units in titles, axis labels, or formatted values. Never expose unexplained
  values like `0.274991` when the user expects `27.5%`.
- Keep body text and marks readable in both the default and any supported dark mode;
  do not hard-code a white card background unless the app intentionally stays light.

Theme-wide color, type, and spacing belong in `ui.Theme`. Local alignment or a
special hero treatment can use a small `ui.tags.style(...)` block or a real CSS file
under `www/`. Avoid a large selector patch that depends on bslib's internal DOM.

## Compose for hierarchy and responsiveness

- Put global filters in the page sidebar; put a display option that affects only one
  chart in that card's toolbar.
- Give every chart, map, and data table a card title and normally
  `full_screen=True`.
- Use `ui.layout_column_wrap(width="240px", fill=False)` for KPI cards that should
  wrap naturally.
- Use responsive `col_widths`, for example
  `{"sm": (12,), "lg": (7, 5)}`, when two analytical cards share a row.
- Avoid more than two substantial charts in one desktop row. Mobile layouts should
  stack without clipped labels or horizontal page scrolling.
- Keep output IDs globally unique, including helpers reused on different nav panels.

## Design useful states

The initial filter state must produce meaningful results. For every renderer, decide
what the user sees while data is loading, when filters produce no rows, and when
optional columns are unavailable.

Use `req()` for a temporary prerequisite that should silently pause downstream work.
For a valid but empty filter result, render an intentional message in the card rather
than leaving a spinner or raising an indexing error. Disable or update dependent
inputs when their choices become invalid.

Format user-facing values consistently:

```python
def fmt_currency(value: float) -> str:
    return f"${value:,.0f}"

def fmt_percent(value: float) -> str:
    return f"{value:.1%}"
```

## Verify function and appearance

Do not call a dashboard complete because the Python process starts. Run it in a real
browser and perform this quality pass:

1. Open every nav panel at a desktop viewport and a narrow/mobile viewport.
2. Exercise every global filter and at least one card-local control.
3. Confirm that all visible outputs update from the same filtered row set.
4. Test a combination that produces no data and recover from it.
5. Expand full-screen cards and close any tooltip, popover, modal, or notification.
6. Check the browser console and server output for errors.
7. Inspect labels, units, number formatting, legends, color meaning, focus order, and
   contrast.
8. Capture a screenshot of each page and fix clipping, accidental blank space,
   touching cards, tiny plots, and visual imbalance.

## Common mistakes

- Starting with CSS before choosing Shiny's page, grid, card, and theme primitives.
- Creating a navbar merely to hide an overcrowded page instead of clarifying tasks.
- Showing KPIs without a period, comparison, or definition.
- Using a map when ranked categories answer the question more clearly.
- Styling each chart independently, producing inconsistent fonts and category colors.
- Checking only the happy path or only the initial tab.
