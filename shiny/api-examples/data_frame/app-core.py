import pandas  # noqa: F401 (this line needed for Shinylive to load plotly.express)
import plotly.express as px
from shinywidgets import output_widget, render_widget

from shiny import App, reactive, render, req, ui

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

app_ui = ui.page_fillable(
    {"class": "p-3"},
    ui.markdown(
        "**Instructions**: Select one or more countries in the table below to see more information."
    ),
    ui.layout_columns(
        ui.card(ui.output_data_frame("summary_data"), height="400px"),
        ui.card(output_widget("country_detail_pop"), height="400px"),
        ui.card(output_widget("country_detail_percap"), height="400px"),
        col_widths=[12, 6, 6],
    ),
)


def server(input, output, session):
    @render.data_frame
    def summary_data():
        return render.DataGrid(summary_df.round(2), row_selection_mode="multiple")

    @reactive.calc
    def filtered_df():
        req(input.summary_data_selected_rows())

        # input.summary_data_selected_rows() is a tuple, so we must convert it to list,
        # as that's what Pandas requires for indexing.
        selected_idx = list(input.summary_data_selected_rows())
        countries = summary_df.iloc[selected_idx]["country"]
        # Filter data for selected countries
        return df[df["country"].isin(countries)]

    @render_widget
    def country_detail_pop():
        return px.line(
            filtered_df(),
            x="year",
            y="pop",
            color="country",
            title="Population Over Time",
        )

    @render_widget
    def country_detail_percap():
        return px.line(
            filtered_df(),
            x="year",
            y="gdpPercap",
            color="country",
            title="GDP per Capita Over Time",
        )


app = App(app_ui, server)
