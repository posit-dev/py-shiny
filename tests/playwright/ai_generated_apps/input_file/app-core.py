import pandas as pd

from shiny import App, reactive, render, ui
from shiny.types import FileInfo

# Define the UI
app_ui = ui.page_fillable(
    # Main card containing file input and table
    ui.card(
        ui.card_header("File Upload Demo"),
        # File input with all possible parameters
        ui.input_file(
            id="file1",
            label="Upload File",
            multiple=True,
            accept=[".csv", ".txt", "text/plain", "application/pdf", "image/*"],
            button_label="Choose Files...",
            placeholder="Multiple files can be selected",
            width="400px",
            capture="user",
        ),
        # Output for the data grid
        ui.output_data_frame("file_table"),
        # Instructions card
        ui.card(
            ui.markdown(
                """
                ### Instructions:
                1. Click 'Choose Files...' to select one or more files
                2. Supported file types: CSV, TXT, PDF, and images
                3. File information will appear in the table below
                4. Use filters to search through uploaded files
                """
            )
        ),
    )
)


# Define the server
def server(input, output, session):
    # Reactive calculation for parsing files
    @reactive.calc
    def parse_files():
        files: list[FileInfo] | None = input.file1()
        if not files:
            return pd.DataFrame()

        # Create a DataFrame with file information
        file_info = []
        for file in files:
            file_info.append(
                {
                    "Name": file["name"],
                    "Size (bytes)": file["size"],
                    "Type": file["type"],
                }
            )
        return pd.DataFrame(file_info)

    # Render the data grid
    @output
    @render.data_frame
    def file_table():
        df = parse_files()
        if df.empty:
            return render.DataGrid(
                pd.DataFrame(columns=["Name", "Size (bytes)", "Type"]),
                height="300px",
                width="100%",
                filters=True,
                selection_mode="row",
            )
        return render.DataGrid(
            df, height="300px", width="100%", filters=True, selection_mode="row"
        )


# Create and return the app
app = App(app_ui, server)
