import pandas as pd
import polars as pl
from narwhals.stable.v1.typing import IntoDataFrame

from shiny import App, Inputs, Outputs, Session, module, reactive, render, ui

# Mock Iris dataset subset for testing to avoid importing seaborn and downloading from GitHub
distinct_df = pd.DataFrame(
    {
        "sepal_length": [5.1, 4.9, 7.0, 6.4, 6.3, 5.8],
        "sepal_width": [3.5, 3.0, 3.2, 3.2, 3.3, 2.7],
        "petal_length": [1.4, 1.4, 4.7, 4.5, 6.0, 5.1],
        "petal_width": [0.2, 0.2, 1.4, 1.5, 2.5, 1.9],
        "species": [
            "setosa",
            "setosa",
            "versicolor",
            "versicolor",
            "virginica",
            "virginica",
        ],
    },
    index=[0, 1, 50, 51, 100, 101],
)
idxs = distinct_df.index.tolist()


@module.ui
def mod_ui():
    return ui.TagList(
        ui.h2("Iris Dataset"),
        ui.layout_column_wrap(
            ui.input_action_button("reset_df", "Reset Dataframe"),
            ui.input_action_button("update_sort", "Update sort"),
            ui.input_action_button("update_filter", "Update filter"),
            width=1 / 3,
        ),
        ui.br(),
        ui.output_data_frame("iris_df"),
        ui.h2("Data view indices"),
        ui.output_text_verbatim("data_view_rows"),
        ui.h2("Indices when view_selected=True"),
        ui.output_text_verbatim("data_view_selected_true"),
        ui.h2("Indices when view_selected=False"),
        ui.output_text_verbatim("data_view_selected_false"),
        ui.h2("Show selected cell"),
        ui.output_text_verbatim("cell_selection"),
        ui.h2("Type:"),
        ui.output_text_verbatim("df_type"),
    )


@module.server
def mod_server(
    input: Inputs,
    output: Outputs,
    session: Session,
    data: IntoDataFrame,
):
    @render.text
    def df_type():
        return str(type(data))

    @render.data_frame
    def iris_df():
        return render.DataGrid(
            data=data,
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

        if isinstance(data_view_all, pd.DataFrame):
            return str(
                [
                    int(val)
                    for val in data_view_all.index.values  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType, reportUnknownArgumentType]
                ]
            )
        elif isinstance(data_view_all, pl.DataFrame):
            return str(data_view_all.get_column("index").to_list())
        else:
            raise ValueError("Invalid data type")

    @render.code
    def data_view_selected_true():  # pyright: ignore[reportUnknownParameterType]
        # TODO-barret; remove type check when DataFrameT is implemented
        data_view_selected = iris_df.data_view(selected=True)

        if isinstance(data_view_selected, pd.DataFrame):
            return str(
                [
                    int(val)
                    for val in data_view_selected.index.values  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType, reportUnknownArgumentType]
                ]
            )
        elif isinstance(data_view_selected, pl.DataFrame):
            return str(data_view_selected["index"].to_list())
        else:
            raise ValueError("Invalid data type")

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


app_ui = ui.page_fluid(
    ui.navset_card_underline(
        ui.nav_panel(
            "pandas",
            mod_ui("pandas"),
        ),
        ui.nav_panel(
            "polars",
            mod_ui("polars"),
        ),
        id="tab",
    ),
)


def server(input: Inputs, output: Outputs, session: Session) -> None:
    mod_server("pandas", distinct_df)
    mod_server(
        "polars", pl.from_pandas(distinct_df).with_columns(pl.Series("index", idxs))
    )


app = App(app_ui, server)
