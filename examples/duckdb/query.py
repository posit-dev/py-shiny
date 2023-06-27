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
                {"style": "font-family: var(--bs-font-monospace); margin-top: 10px;"},
                ui.input_text_area(
                    "sql_query",
                    "",
                    value=qry,
                    width="100%",
                    height="200px",
                ),
            ),
            ui.row(
                {"style": "margin-bottom: 10px;"},
                ui.column(
                    6,
                    ui.input_action_button("run", "Run Query", width="90%"),
                ),
                ui.column(
                    6,
                    ui.input_action_button("rmv", "Remove Query", width="90%"),
                ),
            ),
        ),
        ui.column(9, ui.output_data_frame("results")),
    )

    return out


@module.server
def query_output_server(
    input, output, session, con: duckdb.DuckDBPyConnection, remove_id
):
    result = reactive.Value()

    @reactive.Effect
    @reactive.event(input.run)
    def _():
        qry = input.sql_query().replace("\n", " ")
        res = con.query(qry).to_df()
        result.set(res)

    @output
    @render.data_frame
    def results():
        return result.get()

    @reactive.Effect
    @reactive.event(input.rmv)
    def _():
        ui.remove_ui(selector=f"div#{remove_id}")
