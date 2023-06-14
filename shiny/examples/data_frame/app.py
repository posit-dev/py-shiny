import plotly.express as px
import plotly.graph_objs as go
from shinywidgets import output_widget, render_widget

from shiny import App
from shiny import experimental as x
from shiny import reactive, render, req, ui

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

app_ui = x.ui.page_fillable(
    {"class": "p-3"},
    x.ui.layout_column_wrap(
        1,
        x.ui.card(
            x.ui.card_body(
                ui.output_data_frame("summary_data"),
            ),
        ),
        x.ui.layout_column_wrap(
            1 / 2,
            x.ui.card(
                output_widget("country_detail_pop", height="100%"),
            ),
            x.ui.card(
                output_widget("country_detail_percap", height="100%"),
            ),
        ),
    ),
)


def server(input, output, session):
    @output
    @render.data_frame
    def summary_data():
        return render.DataGrid(
            summary_df.round(2),
            row_selection_mode="multi-toggle",
            height="100%",
        )

    @reactive.Calc
    def filtered_df():
        selected_idx = list(req(input.summary_data_selected_rows()))
        countries = summary_df["country"][selected_idx]
        # Filter data for selected countries
        return df[df["country"].isin(countries)]

    @output
    @render_widget
    def country_detail_pop():
        # Create the plot
        fig = px.line(
            filtered_df(),
            x="year",
            y="pop",
            color="country",
            title="Population Over Time",
        )
        return go.FigureWidget(fig)

    @output
    @render_widget
    def country_detail_percap():
        # Create the plot
        fig = px.line(
            filtered_df(),
            x="year",
            y="gdpPercap",
            color="country",
            title="GDP per Capita Over Time",
        )
        return go.FigureWidget(fig)


app = App(app_ui, server)
