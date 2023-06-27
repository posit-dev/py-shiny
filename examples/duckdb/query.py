import duckdb
import pandas as pd

from shiny import module, reactive, render, ui


@module.ui
def query_output_ui(remove_id, qry="SELECT * from weather LIMIT 10"):
    out = ui.row(
        {
            "style": "border: 1px solid gray; border-radius: 5px; margin:10px",
            "id": remove_id,
        },
        ui.column(
            3,
            ui.div(
                {"style": "font-family: var(--bs-font-monospace)"},
                ui.input_text_area(
                    "sql_query",
                    "",
                    value=qry,
                    width="100%",
                    height="200px",
                ),
            ),
            ui.input_action_button("rmv", "Remove Query"),
        ),
        ui.column(9, ui.output_data_frame("results")),
    )

    return out


@module.server
def query_output_server(
    input, output, session, con: duckdb.DuckDBPyConnection, remove_id
):
    print(remove_id)

    @reactive.Calc
    def response_table():
        qry = input.sql_query().replace("\n", " ")

        return con.query(qry).to_df()

    @output
    @render.data_frame
    def results():
        return response_table()

    @reactive.Effect
    @reactive.event(input.rmv)
    def _():
        ui.remove_ui(selector=f"div#{remove_id}")
