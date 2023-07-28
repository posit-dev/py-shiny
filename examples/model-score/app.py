import sqlite3

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import scoredata
from shinywidgets import output_widget, register_widget, render_widget

import shiny.experimental as x
from shiny import App, Inputs, Outputs, Session, reactive, render, req, ui

# TODO: Make an option to switch between dynamic and static
# TODO: Refresh rate option
# TODO: Add threshold lines (or bg shading) to plot
# TODO: Change "score" to "auc"
# TODO: Talk to Julia and Isabel for suggestions

scoredata.begin()

con = sqlite3.connect(scoredata.SQLITE_DB_URI, uri=True)


def last_modified(con):
    return con.execute("select max(timestamp) from auc_scores").fetchone()[0]


# @reactive.poll calls a cheap query (`last_modified()`) every 1 second to check if the
# expensive query should be run and downstream calculations should be updated
@reactive.poll(lambda: last_modified(con))
def df():
    tbl = pd.read_sql(
        "select * from auc_scores order by timestamp desc, model desc limit ?",
        con,
        params=[150],
    )
    # Treat timestamp as a continuous variable
    tbl["timestamp"] = pd.to_datetime(tbl["timestamp"]).dt.strftime("%H:%M:%S")
    # Reverse order of rows
    tbl = tbl.iloc[::-1]

    return tbl


with reactive.isolate():
    model_names = df()["model"].unique().tolist()
colors = ["#7fc97f", "#beaed4", "#fdc086", "#ffff99", "#386cb0"]
colormap_models = {model: colors[i] for i, model in enumerate(model_names)}


app_ui = x.ui.page_sidebar(
    x.ui.sidebar(
        ui.input_checkbox_group("models", "Models", model_names, selected=model_names),
    ),
    ui.h1("Model monitoring dashboard"),
    # ui.tags.link(
    #     rel="stylesheet",
    #     href="https://rstudio.github.io/shiny-python-workshop-2023/site_libs/bootstrap/bootstrap.min.css",
    # ),
    x.ui.output_ui("cards"),
    x.ui.card(output_widget("plot_timeseries"), class_="mt-3"),
    x.ui.card(output_widget("plot_dist"), class_="mt-3"),
    fillable=False,
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.Calc
    def filtered_df():
        data = df()
        # Filter the rows so we only include the desired models
        return data[data["model"].isin(input.models())]

    @output
    @render.ui
    def cards():
        data = filtered_df()
        models = data["model"].unique().tolist()
        scores_by_model = {
            x: data[data["model"] == x].iloc[-1]["score"] for x in models
        }
        # Round scores to 2 decimal places
        scores_by_model = {x: round(y, 2) for x, y in scores_by_model.items()}

        return x.ui.layout_column_wrap(
            "150px",
            *[
                x.ui.value_box(
                    model,
                    ui.h2(score),
                    theme_color="success"
                    if score > 0.85
                    else "warning"
                    if score > 0.65
                    else "danger",
                )
                for model, score in scores_by_model.items()
            ],
            fixed_width=True,
        )

    # Streaming plotly

    @output
    @render_widget
    @reactive.event(input.models)
    def plot_timeseries():
        # This plotly output will re-render whenever the set of selected models changes,
        # but not when the data changes. Instead, for data changes, we will
        # incrementally update only the traces. This is because the plotly plot
        # sometimes jumps around a bit when the entire plot is redrawn.

        # Create the initial (for this set of selected models) figure. Normally, changes
        # in filtered_df would cause a re-render of the whole plot, but the fact that we
        # decorated this function with @reactive.event(input.models) means that only
        # changes to input.models() can trigger re-rendering.
        fig = px.line(
            filtered_df(),
            x="timestamp",
            y="score",
            labels=dict(score="auc"),
            color="model",
            color_discrete_map=colormap_models,
        )

        fig.update_yaxes(range=[0, 1], fixedrange=True)
        fig.update_xaxes(fixedrange=True, tickangle=60, dtick="M5")
        f = go.FigureWidget(fig)

        # Create a new reactive Effect *for this figure instance* (hence, it's nested
        # within the plot_timeseries function). This effect will re-run whenever its own
        # reactive dependencies change, i.e. filtered_df().
        @reactive.Effect
        def update_plotly_data():
            # Create a new plotly figure with the updated data, that we'll use to update
            # the existing figure. It's important that we use the same arguments as the
            # existing figure, so that all the traces line up.
            f_new = px.line(
                filtered_df(),
                x="timestamp",
                y="score",
                labels=dict(score="auc"),
                color="model",
                color_discrete_map=colormap_models,
            )
            # In one batch, update all the traces in the existing figure with the new
            # ones.
            with f.batch_update():
                for old, new in zip(f.data, f_new.data):
                    old.update(new)

        # Stop updates when this version of the plot is no longer up-to-date
        reactive.get_current_context().on_invalidate(update_plotly_data.destroy)

        return f

    @output
    @render_widget
    @reactive.event(input.models)
    def plot_dist():
        # This works exactly like plot_timeseries, but with a different plot.

        fig = px.histogram(
            filtered_df(),
            facet_row="model",
            nbins=20,
            x="score",
            labels=dict(score="auc"),
            color="model",
            color_discrete_map=colormap_models,
        )
        # From https://plotly.com/python/facet-plots/#customizing-subplot-figure-titles
        fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))

        fig.update_xaxes(range=[0, 1], fixedrange=True)
        fig.layout["height"] = 550

        f = go.FigureWidget(fig)

        @reactive.Effect
        def update_plotly_data():
            f_new = px.histogram(
                filtered_df(),
                facet_row="model",
                nbins=20,
                x="score",
                color="model",
                color_discrete_map=colormap_models,
            )
            with f.batch_update():
                for old, new in zip(f.data, f_new.data):
                    old.update(new)

        reactive.get_current_context().on_invalidate(update_plotly_data.destroy)

        return f


app = App(app_ui, server)
