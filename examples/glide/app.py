import pandas as pd
import seaborn as sns

from shiny import App, Inputs, Outputs, Session, reactive, render, req, ui

app_ui = ui.page_fluid(
    ui.input_select("dataset", "Dataset", sns.get_dataset_names()),
    ui.output_data_grid("grid"),
)


def server(input: Inputs, output: Outputs, session: Session):
    df: reactive.Value[pd.DataFrame] = reactive.Value()

    @reactive.Effect
    def update_df():
        return df.set(sns.load_dataset(req(input.dataset())))

    @output
    @render.table(json=True)
    def grid():
        return df()

    @reactive.Effect
    @reactive.event(input.grid_cell_edit)
    def handle_edit():
        edit = input.grid_cell_edit()
        df_copy = df().copy()
        df_copy.iat[edit["row"], edit["col"]] = edit["new_value"]
        df.set(df_copy)


app = App(app_ui, server)
