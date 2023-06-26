import os
import urllib.request
from pathlib import Path

import duckdb
import shinyswatch.theme as theme
from query import query_output_server, query_output_ui

from shiny import App, reactive, ui

folder = Path(__file__).parent
db_file = folder / "weather.db"

if not Path.exists(db_file):
    csv_url = "https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2022/2022-12-20/weather_forecasts.csv"
    local_file_path = folder / "weather.csv"
    urllib.request.urlretrieve(csv_url, local_file_path)
    con = duckdb.connect(str(db_file), read_only=False)
    con.sql(f"CREATE TABLE weather AS SELECT * FROM read_csv_auto('{local_file_path}')")
    con.close()

con = duckdb.connect(str(db_file), read_only=True)

button_style = {"style": "margin: 15px"}

app_ui = ui.page_fluid(
    theme.flatly(),
    ui.panel_title("DuckDB query explorer"),
    ui.row(
        ui.column(
            2,
            ui.row(
                button_style,
                ui.input_action_button("add_query", "Add Query"),
            ),
            ui.row(
                button_style,
                ui.input_action_button("remove_query", "Remove Query"),
            ),
            ui.br(),
            ui.row(
                ui.p(
                    """
                    This app lets you explore a dataset using SQL and duckdb.
                    The data is stored in an on-disk duckdb database, and as a result
                    the queries fast enough that you don't need a separate button
                    to execute the queries.
                    """
                ),
            ),
        ),
        ui.column(
            10,
            ui.tags.div(query_output_ui("initial_query"), id="module_container"),
        ),
    ),
)


def server(input, output, session):
    mod_counter = reactive.Value(0)

    query_output_server("initial_query", con=con)

    @reactive.Effect
    @reactive.event(input.add_query)
    def _():
        counter = mod_counter.get() + 1
        mod_counter.set(counter)
        id = "query_" + str(counter)
        ui.insert_ui(
            selector="#module_container", where="afterBegin", ui=query_output_ui(id)
        )
        query_output_server(id, con=con)

    @reactive.Effect
    @reactive.event(input.remove_query)
    def _():
        ui.remove_ui(selector=f"#module_container .row:first-child")


app = App(app_ui, server)
