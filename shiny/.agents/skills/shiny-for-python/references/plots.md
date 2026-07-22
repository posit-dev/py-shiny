---
name: plots
description: Covers rendering matplotlib/seaborn/plotnine figures and static images in a Shiny for Python (py-shiny) app with @render.plot and @render.image, plus reading plot click/hover/brush interactions. Use when displaying a figure or image, sizing a plot, making a plot respond to clicks/hover/brush selection, reading which points or region a user selected (input.<id>_click / _brush / _hover), or when tempted to save a figure to a temp PNG and serve it manually, poll for plot clicks, or wire up JavaScript event handlers by hand. For fully interactive JS charts (Plotly/Altair/ipywidgets) use shinywidgets instead.
---

# Rendering plots and images in Shiny for Python

## Overview

Return a figure from a `@render.plot`-decorated function paired with a
`ui.output_plot(id)` placeholder; return an `ImgData` dict from `@render.image`
paired with `ui.output_image(id)` for static image files. Do **not** call
`fig.savefig(tmp.png)` and serve the file yourself — `@render.plot` encodes the
figure for you. Do **not** poll or add JS listeners to detect clicks — instead, enable
`click`/`hover`/`brush` on `output_plot` and read the resulting reactive inputs.

## Render a plot

`@render.plot` accepts a matplotlib `Figure`/`Axes`, a seaborn object (return
its `.figure`), or a plotnine `ggplot`. You may also draw with the pyplot global
interface and return nothing (sync functions only).

```python
import matplotlib.pyplot as plt
import numpy as np
from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.input_slider("n", "Bins", 5, 50, 20),
    ui.output_plot("hist", width="600px", height="400px"),
)

def server(input, output, session):
    @render.plot(alt="A histogram")
    def hist():
        fig, ax = plt.subplots()
        ax.hist(np.random.randn(500), bins=input.n())
        return fig

app = App(app_ui, server)
```

Set the display size on `ui.output_plot(width=, height=)` (CSS units; the plot
auto-fits). `@render.plot(alt=...)` sets screen-reader text; `@render.plot(width=,
height=)` forces a pixel size and is rarely needed. Extra kwargs pass through to
the backend's save method (e.g. matplotlib `savefig`). In Express, the same
decorator works inline with no `output_plot` call — see the `express` skill.

## Render a static image

Return an `ImgData` dict (`src` required; optional `width`/`height`/`alt`).
Use `@render.image(delete_file=True)` to remove a generated temp file after
sending.

```python
from pathlib import Path
from shiny import render, ui
from shiny.types import ImgData

# ui: ui.output_image("logo")
@render.image
def logo() -> ImgData:
    return {"src": str(Path(__file__).parent / "logo.png"), "width": "200px"}
```

## Read plot interactions

Enable interaction on the output container. Each enabled event exposes a reactive
input named `input.<id>_<event>()`:

```python
ui.output_plot("scatter", click=True, brush=True)
```

- `input.scatter_click()` → `{"x": ..., "y": ...}` in data coordinates (also
  `dblclick`, `hover`).
- `input.scatter_brush()` → `{"xmin", "xmax", "ymin", "ymax", ...}`.

Both are `None` until the user acts. Pass `ui.click_opts()`, `ui.hover_opts()`,
`ui.dblclick_opts()`, or `ui.brush_opts(direction="x")` instead of `True` to tune
behavior.

## Map interactions back to data rows

Do not compute hit-testing yourself. `shiny.plotutils.near_points` (click/hover)
and `brushed_points` (brush) return the underlying `DataFrame` rows, inferring
`xvar`/`yvar` from the plot mapping when possible (always inferable for plotnine;
supply them explicitly for matplotlib/seaborn).

```python
import matplotlib.pyplot as plt
from shiny import App, reactive, render, ui
from shiny.plotutils import brushed_points, near_points
import pandas as pd

df = pd.DataFrame({"wt": [2, 3, 4, 5], "mpg": [30, 25, 20, 15]})

app_ui = ui.page_fluid(
    ui.output_plot("p", click=True, brush=True),
    ui.output_data_frame("selected"),
)

def server(input, output, session):
    @render.plot
    def p():
        fig, ax = plt.subplots()
        ax.scatter(df["wt"], df["mpg"])
        return fig

    @render.data_frame
    def selected():
        brush = brushed_points(df, input.p_brush(), xvar="wt", yvar="mpg")
        if not brush.empty:
            return brush
        return near_points(df, input.p_click(), xvar="wt", yvar="mpg")

app = App(app_ui, server)
```

`all_rows=True` returns every row with a boolean `selected_` column instead of
filtering.

## Quick reference

| Item | Value |
|---|---|
| Renderers | `@render.plot(alt=, width=, height=, **savefig_kwargs)`, `@render.image(delete_file=)` |
| Containers | `ui.output_plot(id, width=, height=, click=, dblclick=, hover=, brush=)`, `ui.output_image(...)` |
| Supported figures | matplotlib `Figure`/`Axes`, seaborn (`.figure`), plotnine `ggplot`, PIL `Image` |
| Interaction inputs | `input.<id>_click()`, `_dblclick()`, `_hover()` → `{x, y}`; `_brush()` → `{xmin, xmax, ymin, ymax}` |
| Option builders | `ui.click_opts()`, `ui.dblclick_opts()`, `ui.hover_opts()`, `ui.brush_opts(direction=, delay=, ...)` |
| Row selection | `plotutils.near_points(df, input.<id>_click(), xvar=, yvar=)`, `plotutils.brushed_points(df, input.<id>_brush(), ...)` |
| `ImgData` keys | `src` (required), `width`, `height`, `alt`, `coordmap` |

## Common mistakes

- Saving to a temp PNG and serving it → return the `Figure` from `@render.plot`;
  it encodes the image itself. Only static files on disk need `@render.image`.
- Interaction input always `None` → you did not enable it on `output_plot`
  (`click=True`, `brush=True`, ...); the flag lives on the container, not the renderer.
- Wrong input name → it is `input.<id>_brush()` / `_click()`, not `input.<id>()`.
- `near_points`/`brushed_points` raising "not able to infer `xvar`" → for
  matplotlib/seaborn pass `xvar=`/`yvar=` explicitly (only plotnine auto-infers).
- Async `@render.plot` erroring on pyplot → the global pyplot interface is unsafe
  in async functions; build and return a `Figure` object instead.
- Reaching for `@render.plot` to get zoom/tooltips/pan → those are static images;
  use shinywidgets with Plotly/Altair/ipywidgets for client-side interactivity.
