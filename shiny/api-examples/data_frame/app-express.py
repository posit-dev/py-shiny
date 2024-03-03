import pandas  # noqa: F401 (this line needed for Shinylive to load plotly.express)
import plotly.express as px
from shinywidgets import render_widget

from shiny import reactive, req
from shiny.express import input, render, ui

# Load the Gapminder dataset
df = px.data.gapminder()

# Prepare a summary DataFrame
summary_df = (
    df.groupby("country")
    .agg(
        {
            "pop": ["min", "max", "mean"],
            "lifeExp": ["min", "max", "mean"],
            "gdpPercap": ["min", "max", "mean"],
        }
    )
    .reset_index()
)

summary_df.columns = ["_".join(col).strip() for col in summary_df.columns.values]
summary_df.rename(columns={"country_": "country"}, inplace=True)

# Set up the UI

ui.page_opts(fillable=True)

ui.markdown(
    "**Instructions**: Select one or more countries in the table below to see more information."
)

with ui.layout_columns(col_widths=[12, 6, 6]):
    with ui.card(height="400px"):

        @render.data_frame
        def summary_data():
            return render.DataGrid(summary_df.round(2), row_selection_mode="multiple")

    with ui.card(height="400px"):

        @render_widget
        def country_detail_pop():
            return px.line(
                filtered_df(),
                x="year",
                y="pop",
                color="country",
                title="Population Over Time",
            )

    with ui.card(height="400px"):

        @render_widget
        def country_detail_percap():
            return px.line(
                filtered_df(),
                x="year",
                y="gdpPercap",
                color="country",
                title="GDP per Capita Over Time",
            )


@reactive.calc
def filtered_df():
    req(input.summary_data_selected_rows())

    # input.summary_data_selected_rows() is a tuple, so we must convert it to list,
    # as that's what Pandas requires for indexing.

    selected_idx = list(input.summary_data_selected_rows())
    countries = summary_df.iloc[selected_idx]["country"]
    # Filter data for selected countries
    return df[df["country"].isin(countries)]
