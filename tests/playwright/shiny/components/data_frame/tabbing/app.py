import pandas as pd
import polars as pl

from shiny import App, Inputs, Outputs, Session, render, ui

# Mock Iris dataset subset for testing to avoid importing seaborn and downloading from GitHub
df = pd.DataFrame(
    {
        "sepal_length": [5.1, 4.9, 4.7, 4.6, 5.0],
        "sepal_width": [3.5, 3.0, 3.2, 3.1, 3.6],
        "petal_length": [1.4, 1.4, 1.3, 1.5, 1.4],
        "petal_width": [0.2, 0.2, 0.2, 0.2, 0.2],
        "species": ["setosa", "setosa", "setosa", "setosa", "setosa"],
    }
)
pl_df = pl.from_pandas(df)
df["sepal_length"] = df["sepal_length"].apply(lambda x: ui.tags.u(x))  # pyright: ignore
df["sepal_width"] = df["sepal_width"].apply(lambda x: ui.tags.u(x))  # pyright: ignore
df["petal_width"] = df["petal_width"].apply(lambda x: ui.tags.u(x))  # pyright: ignore
df["species"] = df["species"].apply(lambda x: ui.tags.u(x))  # pyright: ignore

pl_df = pl_df.with_columns(
    (pl.Series([ui.tags.u(x) for x in pl_df["sepal_length"].to_list()])).alias(
        "sepal_length"
    ),
    (pl.Series([ui.tags.u(x) for x in pl_df["sepal_width"].to_list()])).alias(
        "sepal_width"
    ),
    (pl.Series([ui.tags.u(x) for x in pl_df["petal_width"].to_list()])).alias(
        "petal_width"
    ),
    (pl.Series([ui.tags.u(x) for x in pl_df["species"].to_list()])).alias("species"),
)

app_ui = ui.page_fluid(
    ui.navset_card_underline(
        ui.nav_panel("pandas", ui.output_data_frame("pandas_iris")),
        ui.nav_panel("polars", ui.output_data_frame("polars_iris")),
        id="tab",
    ),
)


def server(input: Inputs, output: Outputs, session: Session) -> None:

    @render.data_frame
    def pandas_iris():
        return render.DataGrid(
            data=df.head(),  # pyright: ignore[reportUnknownArgumentType]
            editable=True,
        )

    @render.data_frame
    def polars_iris():
        return render.DataGrid(
            data=pl_df.head(),  # pyright: ignore[reportUnknownArgumentType]
            editable=True,
        )


app = App(app_ui, server)
