import duckdb

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
    @render.data_frame
    def results():
        # In order to avoid the query re-running with each keystroke we
        # wrap it in isolate and add a call to `input.run()` to trigger execution.
        # This ensures that the query runs when the module is populated and also
        # passes the error messages on to the user.
        input.run()
        with reactive.isolate():
            qry = input.sql_query().replace("\n", " ")
            result = con.query(qry).to_df()

        return result

    @reactive.effect
    @reactive.event(input.rmv)
    def _():
        ui.remove_ui(selector=f"div#{remove_id}")
