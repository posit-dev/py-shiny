import duckdb
import pandas as pd

from shiny import module, reactive, render, ui


@module.ui
def query_output_ui(qry="SELECT * from weather LIMIT 10"):
    out = ui.row(
        {"style": "border: 1px solid gray; border-radius: 5px; margin:10px"},
        ui.column(
            3,
            ui.input_text_area(
                "sql_query",
                "",
                value=qry,
                width="100%",
                height="200px",
            ),
        ),
        ui.column(9, ui.output_data_frame("results")),
    )

    return out


@module.server
def query_output_server(input, output, session, con: duckdb.DuckDBPyConnection):
    @reactive.Calc
    def response_table():
        if input.sql_query() == "":
            return pd.DataFrame()
        qry = input.sql_query().replace("\n", "")

        return con.query(qry).to_df()

    @output
    @render.data_frame
    def results():
        return response_table()
