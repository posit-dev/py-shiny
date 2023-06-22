import pandas as pd

from shiny import App, reactive, render, ui

app_ui = ui.page_fluid(
    ui.input_file("file", "File", accept=".csv"),
    ui.input_checkbox("row_count", "Row count", False),
    ui.input_checkbox("column_count", "Column count", False),
    ui.input_checkbox("column_names", "Column names", False),
    ui.output_table("summary"),
)


def server(input, output, session):
    # Reading in the data into a reactive calcuation makes it easier to work with
    @reactive.Calc
    def parsed_file():
        file = input.file()
        if file is None:
            # Returning an empty dataframe is a bit simpler than the conditional UI
            return pd.DataFrame()
        return pd.read_csv(file[0]["datapath"])

    @output
    @render.table
    def summary():
        df = parsed_file()

        if df.empty:
            return pd.DataFrame()

        # Get the row count, column count, and column names of the DataFrame
        row_count = df.shape[0]
        column_count = df.shape[1]
        names = df.columns.tolist()
        column_names = ", ".join(str(name) for name in names)

        # Create a new DataFrame to display the information
        info_df = pd.DataFrame(
            {
                "Row Count": [row_count],
                "Column Count": [column_count],
                "Column Names": [column_names],
            }
        )

        # return only selected columns based on input
        inputs = [input.row_count(), input.column_count(), input.column_names()]

        index_of_false = []
        for index, element in enumerate(inputs):
            if not element:
                index_of_false.append(index)

        if index_of_false is not None:
            return info_df.drop(info_df.columns[index_of_false], axis=1)

        return info_df


app = App(app_ui, server)
