# Interactive charts with Plotly and shinywidgets

## Overview

Use Plotly through `shinywidgets` when users benefit from tooltips, zooming, legend
filtering, or client-side selection. Use `@render.plot` instead when a static
matplotlib, seaborn, or plotnine image is sufficient. Do not return a Plotly figure
from `@render.plot` or place it in `ui.output_plot()`.

Install the optional chart stack used by the app:

```text
shiny
shinywidgets
plotly
pandas
```

## Contents

- Render a Plotly figure
- Match chart form to the question
- Apply one visual system
- Format labels and hover content
- Handle empty and large data
- Common mistakes

## Render a Plotly figure

In Core mode, pair `output_widget()` in the UI with `@render_plotly` in the server.

```python
import plotly.express as px
from shiny import App, ui
from shinywidgets import output_widget, render_plotly

app_ui = ui.page_fluid(
    ui.card(
        ui.card_header("Revenue by region"),
        output_widget("revenue_by_region"),
        full_screen=True,
    )
)

def server(input, output, session):
    @render_plotly
    def revenue_by_region():
        summary = sales.groupby("region", as_index=False)["revenue"].sum()
        summary = summary.sort_values("revenue")
        fig = px.bar(
            summary,
            x="revenue",
            y="region",
            orientation="h",
            color_discrete_sequence=["#2c7be5"],
            labels={"revenue": "Revenue", "region": "Region"},
        )
        fig.update_layout(template="plotly_white", showlegend=False)
        return fig

app = App(app_ui, server)
```

In Express mode, define the decorated output where it should appear:

```python
from shiny.express import ui
from shinywidgets import render_plotly

with ui.card(full_screen=True):
    ui.card_header("Revenue by region")

    @render_plotly
    def revenue_by_region():
        return make_revenue_figure(filtered_sales())
```

## Match chart form to the question

| Question | Default form |
|---|---|
| Change over time | Line chart; area only when magnitude/volume is the point |
| Compare categories | Sorted horizontal bars |
| Relationship between measures | Scatter plot, with opacity for overlap |
| Distribution | Histogram, box plot, or violin plot |
| Part of a whole | Stacked bar; donut only for a few stable categories |
| Exact record lookup | Data grid/table, not a chart |

Aggregate before plotting. Limit categorical colors and combine or filter long tails
when labels become unreadable. Do not use a second y-axis unless the relationship is
explicit and the scales cannot be confused.

## Apply one visual system

Define a short palette and stable category mapping once. Pass it to every Plotly
Express call instead of accepting a different default sequence in each chart.

```python
PALETTE = ["#2c7be5", "#00a28a", "#f0a202", "#d1495b", "#6f42c1"]
STATUS_COLORS = {
    "On track": "#00a28a",
    "At risk": "#f0a202",
    "Off track": "#d1495b",
}

fig = px.bar(
    summary,
    x="team",
    y="projects",
    color="status",
    color_discrete_map=STATUS_COLORS,
    category_orders={"status": list(STATUS_COLORS)},
)
```

Start with `template="plotly_white"` or register a shared template. Use muted
gridlines, readable axis labels, consistent margins, and a horizontal legend when it
fits. Remove a legend that merely repeats direct category labels. Plotly figures
resize with their widget container; set card or widget height when the surrounding
fillable layout cannot infer a useful size.

## Format labels and hover content

Show the unit in an axis title or tick format, and use direct labels where they reduce
lookup effort without creating clutter.

```python
fig.update_traces(
    texttemplate="%{x:$,.0f}",
    textposition="outside",
    hovertemplate="%{y}<br>Revenue: %{x:$,.0f}<extra></extra>",
)
fig.update_layout(margin={"l": 20, "r": 40, "t": 20, "b": 20})
```

Use `hover_name` and a small `hover_data` mapping for scatter plots. Do not expose
internal IDs or every dataframe column. Clean or omit missing values used for axes,
color, size, labels, and hover fields before constructing the figure.

## Handle empty and large data

Check the filtered frame before calling Plotly. For a valid empty result, return a
simple annotation-only `plotly.graph_objects.Figure` or render an adjacent UI message;
do not allow `min()`, `max()`, or indexing to raise.

For large point clouds, sample or aggregate before rendering. Thousands of SVG marks,
long hover payloads, and many categorical traces can make the browser sluggish even
when the server calculation is fast. Use a density/hexbin view or a WebGL trace when
individual points are not all required.

## Common mistakes

- Pairing a Plotly figure with `@render.plot` / `ui.output_plot`.
- Repeating data filtering inside each chart rather than reading one reactive calc.
- Letting one category change color between charts.
- Encoding the same category in both color and a redundant legend/title.
- Rendering an empty frame without an intentional state.
- Creating many traces or sending unused hover columns to the browser.
