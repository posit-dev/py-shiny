import pandas as pd
import seaborn as sns

from shiny import App, Inputs, Outputs, Session, reactive, render, ui

df = pd.DataFrame(
    sns.load_dataset(  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
        "iris"
    )  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
)

distinct_df = df.drop_duplicates(subset=["species"])
distinct_df = df.iloc[[0, 1, 50, 51, 100, 101]]

app_ui = ui.page_fluid(
    ui.h2("Iris Dataset"),
    ui.layout_column_wrap(
        ui.input_action_button("reset_df", "Reset Dataframe"),
        ui.input_action_button("update_sort", "Update sort"),
        ui.input_action_button("update_filter", "Update filter"),
    ),
    ui.output_data_frame("iris_df"),
    ui.h2("Data view indices"),
    ui.output_text_verbatim("data_view_rows"),
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
            data=distinct_df,
            filters=True,
            selection_mode="rows",
        )

    @render.code
    def data_view_rows():
        return str(iris_df.data_view_rows())

    @render.code
    def data_view_selected_false():  # pyright: ignore[reportUnknownParameterType]
        # TODO-barret; remove type check when DataFrameT is implemented
        data_view_all = iris_df.data_view(selected=False)
        assert isinstance(data_view_all, pd.DataFrame)
        return str(
            data_view_all.index.values  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType, reportUnknownArgumentType]
        )

        return str(
            iris_df.data_view(
                selected=False
            ).index.values  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType, reportUnknownArgumentType]
        )

    @render.code
    def data_view_selected_true():  # pyright: ignore[reportUnknownParameterType]
        # TODO-barret; remove type check when DataFrameT is implemented
        data_view_selected = iris_df.data_view(selected=True)
        assert isinstance(data_view_selected, pd.DataFrame)
        return str(
            data_view_selected.index.values  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType, reportUnknownArgumentType]
        )
        return str(
            iris_df.data_view(
                selected=True
            ).index.values  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType, reportUnknownArgumentType]
        )

    @render.code
    def cell_selection():  # pyright: ignore[reportUnknownParameterType]
        return str(iris_df.cell_selection()["rows"])

    @reactive.effect
    @reactive.event(input.reset_df)
    def reset_df():
        iris_df._reset_reactives()

    @reactive.effect
    @reactive.event(input.update_sort)
    async def update_sort():
        await iris_df.update_sort([1, {"col": 2, "desc": False}])

    @reactive.effect
    @reactive.event(input.update_filter)
    async def update_filter():
        await iris_df.update_filter(
            [{"col": 0, "value": [5, 6.9]}, {"col": 4, "value": "v"}]
        )


app = App(app_ui, server)
