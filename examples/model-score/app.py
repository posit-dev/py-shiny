from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone

import pandas as pd
import plotly.express as px
import scoredata
from plotly_streaming import render_plotly_streaming
from shinywidgets import output_widget

from shiny import App, Inputs, Outputs, Session, reactive, render, ui

THRESHOLD_MID = 0.85
THRESHOLD_MID_COLOR = "rgb(0, 137, 26)"
THRESHOLD_LOW = 0.5
THRESHOLD_LOW_COLOR = "rgb(193, 0, 0)"

# Start a background thread that writes fake data to the SQLite database every second
scoredata.begin()

con = sqlite3.connect(scoredata.SQLITE_DB_URI, uri=True)


def last_modified(con):
    """
    Fast-executing call to get the timestamp of the most recent row in the database.
    We will poll against this in absence of a way to receive a push notification when
    our SQLite database changes.
    """
    return con.execute("select max(timestamp) from accuracy_scores").fetchone()[0]


@reactive.poll(lambda: last_modified(con))
def df():
    """
    @reactive.poll calls a cheap query (`last_modified()`) every 1 second to check if
    the expensive query (`df()`) should be run and downstream calculations should be
    updated.

    By declaring this reactive object at the top-level of the script instead of in the
    server function, all sessions are sharing the same object, so the expensive query is
    only run once no matter how many users are connected.
    """
    tbl = pd.read_sql(
        "select * from accuracy_scores order by timestamp desc, model desc limit ?",
        con,
        params=[150],
    )
    # Convert timestamp to datetime object, which SQLite doesn't support natively
    tbl["timestamp"] = pd.to_datetime(
        tbl["timestamp"], utc=True, format="%Y-%m-%d %H:%M:%S.%f"
    )
    # Create a short label for readability
    tbl["time"] = tbl["timestamp"].dt.strftime("%H:%M:%S")
    # Reverse order of rows
    tbl = tbl.iloc[::-1]

    return tbl


def read_time_period(from_time, to_time):
    tbl = pd.read_sql(
        "select * from accuracy_scores where timestamp between ? and ? order by timestamp, model",
        con,
        params=[from_time, to_time],
    )
    # Treat timestamp as a continuous variable
    tbl["timestamp"] = pd.to_datetime(
        tbl["timestamp"], utc=True, format="%Y-%m-%d %H:%M:%S.%f"
    )
    tbl["time"] = tbl["timestamp"].dt.strftime("%H:%M:%S")

    return tbl


model_names = ["model_1", "model_2", "model_3", "model_4"]
model_colors = {
    name: color
    for name, color in zip(model_names, px.colors.qualitative.D3[0 : len(model_names)])
}


def app_ui(req):
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(minutes=1)

    return ui.page_sidebar(
        ui.sidebar(
            ui.input_checkbox_group(
                "models", "Models", model_names, selected=model_names
            ),
            ui.input_radio_buttons(
                "timeframe",
                "Timeframe",
                ["Latest", "Specific timeframe"],
                selected="Latest",
            ),
            ui.panel_conditional(
                "input.timeframe === 'Latest'",
                ui.input_selectize(
                    "refresh",
                    "Refresh interval",
                    {
                        0: "Realtime",
                        5: "5 seconds",
                        15: "15 seconds",
                        30: "30 seconds",
                        60 * 5: "5 minutes",
                        60 * 15: "15 minutes",
                    },
                ),
            ),
            ui.panel_conditional(
                "input.timeframe !== 'Latest'",
                ui.input_slider(
                    "timerange",
                    "Time range",
                    min=start_time,
                    max=end_time,
                    value=[start_time, end_time],
                    step=timedelta(seconds=1),
                    time_format="%H:%M:%S",
                ),
            ),
        ),
        ui.div(
            ui.h1("Model monitoring dashboard"),
            ui.p(
                ui.output_ui("value_boxes"),
            ),
            ui.card(output_widget("plot_timeseries")),
            ui.card(output_widget("plot_dist")),
            style="max-width: 800px;",
        ),
        fillable=False,
    )


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.calc
    def recent_df():
        """
        Returns the most recent rows from the database, at the refresh interval
        requested by the user. If the refresh interview is 0, go at maximum speed.
        """
        refresh = int(input.refresh())
        if refresh == 0:
            return df()
        else:
            # This approach works well if you know that input.refresh() is likely to be
            # a longer interval than the underlying changing data source (df()). If not,
            # then this can cause downstream reactives to be invalidated when they
            # didn't need to be.
            reactive.invalidate_later(refresh)
            with reactive.isolate():
                return df()

    @reactive.calc
    def timeframe_df():
        """
        Returns rows from the database within the specified time range. Notice that we
        implement the business logic as a separate function (read_time_period), so it's
        easier to reason about and test.
        """
        start, end = input.timerange()
        return read_time_period(start, end)

    @reactive.calc
    def filtered_df():
        """
        Return the data frame that should be displayed in the app, based on the user's
        input. This will be either the latest rows, or a specific time range. Also
        filter out rows for models that the user has deselected.
        """
        data = recent_df() if input.timeframe() == "Latest" else timeframe_df()

        # Filter the rows so we only include the desired models
        return data[data["model"].isin(input.models())]

    @reactive.calc
    def filtered_model_names():
        return filtered_df()["model"].unique()

    @render.ui
    def value_boxes():
        data = filtered_df()
        models = data["model"].unique().tolist()
        scores_by_model = {
            x: data[data["model"] == x].iloc[-1]["score"] for x in models
        }
        # Round scores to 2 decimal places
        scores_by_model = {x: round(y, 2) for x, y in scores_by_model.items()}

        return ui.layout_column_wrap(
            *[
                # For each model, return a value_box with the score, colored based on
                # how high the score is.
                ui.value_box(
                    model,
                    ui.h2(score),
                    theme=(
                        "text-success"
                        if score > THRESHOLD_MID
                        else "text-warning" if score > THRESHOLD_LOW else "bg-danger"
                    ),
                )
                for model, score in scores_by_model.items()
            ],
            width="135px",
            fixed_width=True,
        )

    @render_plotly_streaming(recreate_key=filtered_model_names, update="data")
    def plot_timeseries():
        """
        Returns a Plotly Figure visualization. Streams new data to the Plotly widget in
        the browser whenever filtered_df() updates, and completely recreates the figure
        when filtered_model_names() changes (see recreate_key=... above).
        """
        fig = px.line(
            filtered_df(),
            x="time",
            y="score",
            labels=dict(score="accuracy"),
            color="model",
            color_discrete_map=model_colors,
            # The default for render_mode is "auto", which switches between
            # type="scatter" and type="scattergl" depending on the number of data
            # points. Switching that value breaks streaming updates, as the type
            # property is read-only. Setting it to "webgl" keeps the type consistent.
            render_mode="webgl",
            template="simple_white",
        )

        fig.add_hline(
            THRESHOLD_LOW,
            line_dash="dash",
            line=dict(color=THRESHOLD_LOW_COLOR, width=2),
            opacity=0.3,
        )
        fig.add_hline(
            THRESHOLD_MID,
            line_dash="dash",
            line=dict(color=THRESHOLD_MID_COLOR, width=2),
            opacity=0.3,
        )

        fig.update_yaxes(range=[0, 1], fixedrange=True)
        fig.update_xaxes(fixedrange=True, tickangle=60)

        return fig

    @render_plotly_streaming(recreate_key=filtered_model_names, update="data")
    def plot_dist():
        fig = px.histogram(
            filtered_df(),
            facet_row="model",
            nbins=20,
            x="score",
            labels=dict(score="accuracy"),
            color="model",
            color_discrete_map=model_colors,
            template="simple_white",
        )

        fig.add_vline(
            THRESHOLD_LOW,
            line_dash="dash",
            line=dict(color=THRESHOLD_LOW_COLOR, width=2),
            opacity=0.3,
        )
        fig.add_vline(
            THRESHOLD_MID,
            line_dash="dash",
            line=dict(color=THRESHOLD_MID_COLOR, width=2),
            opacity=0.3,
        )

        # From https://plotly.com/python/facet-plots/#customizing-subplot-figure-titles
        fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))

        fig.update_yaxes(matches=None)
        fig.update_xaxes(range=[0, 1], fixedrange=True)
        fig.layout.height = 500

        return fig

    @reactive.effect
    def update_time_range():
        """
        Every 5 seconds, update the custom time range slider's min and max values to
        reflect the current min and max values in the database.
        """

        reactive.invalidate_later(15)
        try:
            min_time, max_time = pd.to_datetime(
                con.execute(
                    "select min(timestamp), max(timestamp) from accuracy_scores"
                ).fetchone(),
                utc=True,
            )
            ui.update_slider(
                "timerange",
                min=min_time.replace(tzinfo=timezone.utc),
                max=max_time.replace(tzinfo=timezone.utc),
            )
        except sqlite3.OperationalError:
            # Sometimes this executes before the background thread has had a
            # chance to even create the sample data table. In that case, just
            # ignore the error and try again later.
            pass


app = App(app_ui, server)
