import typing

import pandas as pd

from shiny import App, Inputs, Outputs, Session, reactive, render, req, ui
from shiny.types import FileInfo

app_ui = ui.page_fluid(
    ui.input_file("file1", "Choose CSV File", accept=[".csv"], multiple=False),
    ui.input_checkbox_group(
        "stats",
        "Summary Stats",
        choices=["Row Count", "Column Count", "Column Names"],
        selected=["Row Count", "Column Count", "Column Names"],
    ),
    ui.output_table("summary"),
    ui.input_file("file2", "Multiple files", multiple=True),
    ui.output_text_verbatim("file2_info", placeholder=True),
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.calc
    def parsed_file():
        file: typing.Union[typing.List["FileInfo"], None] = input.file1()
        if file is None:
            return pd.DataFrame()
        return pd.read_csv(  # pyright: ignore[reportUnknownMemberType]
            file[0]["datapath"]
        )

    @render.table
    def summary():
        df = parsed_file()

        if df.empty:
            return pd.DataFrame()

        # Get the row count, column count, and column names of the DataFrame
        row_count = df.shape[0]
        column_count = df.shape[1]
        names: list[
            str
        ] = df.columns.tolist()  # pyright: ignore[reportUnknownMemberType]
        column_names = ", ".join(str(name) for name in names)

        # Create a new DataFrame to display the information
        info_df = pd.DataFrame(
            {
                "Row Count": [row_count],
                "Column Count": [column_count],
                "Column Names": [column_names],
            }
        )

        # input.stats() is a list of strings; subset the columns based on the selected
        # checkboxes
        return info_df.loc[:, input.stats()]

    @render.text
    def file2_info():
        file2: typing.Union[typing.List["FileInfo"], None] = input.file2()
        if not file2:
            req(file2)
            return

        req(file2)

        ret = [
            f"File name: {file['name']}\nFile type: {file['type']}\nFile size: {file['size']} bytes"
            for file in file2
        ]

        return "\n---\n".join(ret)


app = App(app_ui, server)
