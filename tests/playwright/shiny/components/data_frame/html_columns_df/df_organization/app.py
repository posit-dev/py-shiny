import pandas as pd
import seaborn as sns

from shiny import App, Inputs, Outputs, Session, reactive, render, ui

df = pd.DataFrame(
    sns.load_dataset(  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
        "iris"
    )  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
)

distinct_df = df.drop_duplicates(subset=["species"])
app_ui = ui.page_fluid(
    ui.row(
        ui.column(
            6,
            ui.h2("Iris Dataset"),
        ),
        ui.column(2, ui.input_action_button("reset_df", "Reset Dataframe")),
    ),
    ui.output_data_frame("iris_df"),
    ui.h2("Data view indices"),
    ui.output_text_verbatim("data_view_indices"),
    ui.h2("Indices when view_selected=True"),
    ui.output_text_verbatim("data_view_selected_true"),
    ui.h2("Indices when view_selected=False"),
    ui.output_text_verbatim("data_view_selected_false"),
    ui.h2("Show selected cell"),
    ui.output_text_verbatim("cell_selection"),
)


def server(input: Inputs, output: Outputs, session: Session) -> None:

    @render.data_frame
    def iris_df():
        return render.DataGrid(
            data=distinct_df,  # pyright: ignore[reportUnknownArgumentType]
            filters=True,
            selection_mode="rows",
        )

    @render.code  # pyright: ignore[reportArgumentType]
    def data_view_indices():
        return iris_df._input_data_view_indices()

    @render.code  # pyright: ignore[reportArgumentType]
    def data_view_selected_false():  # pyright: ignore[reportUnknownParameterType]
        return iris_df.data_view(
            selected=False
        ).index.values  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]

    @render.code  # pyright: ignore[reportArgumentType]
    def data_view_selected_true():  # pyright: ignore[reportUnknownParameterType]
        return iris_df.data_view(
            selected=True
        ).index.values  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]

    @render.code  # pyright: ignore[reportArgumentType]
    def cell_selection():  # pyright: ignore[reportUnknownParameterType]
        return iris_df.input_cell_selection()["rows"]  # pyright: ignore

    @reactive.Effect
    @reactive.event(input.reset_df)
    def reset_df():
        iris_df._reset_reactives()


app = App(app_ui, server)
