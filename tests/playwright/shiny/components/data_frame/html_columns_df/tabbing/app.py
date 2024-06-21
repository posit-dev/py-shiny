import pandas as pd
import seaborn as sns

from shiny import App, Inputs, Outputs, Session, render, ui

df = pd.DataFrame(
    sns.load_dataset(  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
        "iris"
    )
)
app_ui = ui.page_fluid(
    ui.h2("Iris Dataset"),
    ui.output_data_frame("iris_df"),
)

df["sepal_length"] = df["sepal_length"].apply(lambda x: ui.HTML(f"<u>{x}</u>"))  # type: ignore
df["sepal_width"] = df["sepal_width"].apply(lambda x: ui.HTML(f"<u>{x}</u>"))  # type: ignore
df["petal_width"] = df["petal_width"].apply(lambda x: ui.HTML(f"<u>{x}</u>"))  # type: ignore
df["species"] = df["species"].apply(lambda x: ui.HTML(f"<u>{x}</u>"))  # type: ignore


def server(input: Inputs, output: Outputs, session: Session) -> None:

    @render.data_frame
    def iris_df():
        return render.DataGrid(
            data=df.head(),  # pyright: ignore[reportUnknownArgumentType]
            editable=True,
        )


app = App(app_ui, server)
