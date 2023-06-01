import pandas as pd
import seaborn as sns
from shinyswatch.theme import darkly

from shiny import App, Inputs, Outputs, Session, reactive, render, req, ui
from shiny.render import DataGrid


def app_ui(req):
    dark = True if "dark" in req.query_params else None

    return ui.page_fluid(
        ui.head_content(
            ui.tags.meta(name="viewport", content="width=device-width, initial-scale=1")
        ),
        darkly() if dark else None,
        light_dark_switcher(dark),
        ui.input_select("dataset", "Dataset", sns.get_dataset_names()),
        ui.input_select(
            "selection_mode",
            "Selection mode",
            {"none": "(None)", "single": "Single", "multi-toggle": "Multiple"},
            selected="multi-toggle",
        ),
        ui.output_data_grid("grid"),
        ui.panel_absolute(
            ui.output_text_verbatim("detail"),
            right="10px",
            bottom="10px",
        ),
        class_="p-3",
    )


def light_dark_switcher(dark):
    return (
        ui.div(
            ui.a(
                {"class": "btn-primary" if not dark else "btn-outline-primary"},
                "Light",
                href="?" if dark else None,
                class_="btn",
            ),
            ui.a(
                {"class": "btn-primary" if dark else "btn-outline-primary"},
                "Dark",
                href="?dark=1" if not dark else None,
                class_="btn",
            ),
            class_="float-end btn-group",
        ),
    )


def server(input: Inputs, output: Outputs, session: Session):
    df: reactive.Value[pd.DataFrame] = reactive.Value()

    @reactive.Effect
    def update_df():
        return df.set(sns.load_dataset(req(input.dataset())))

    @output
    @render.data_grid
    def grid():
        return DataGrid(df(), row_selection_mode=input.selection_mode())

    @reactive.Effect
    @reactive.event(input.grid_cell_edit)
    def handle_edit():
        edit = input.grid_cell_edit()
        df_copy = df().copy()
        df_copy.iat[edit["row"], edit["col"]] = edit["new_value"]
        df.set(df_copy)

    @output
    @render.text
    def detail():
        if input.grid_row_selection() is not None:
            # "split", "records", "index", "columns", "values", "table"

            return (
                df()
                .iloc[list(input.grid_row_selection())]
                .to_json(None, orient="records", indent=2)
            )


app = App(app_ui, server)
