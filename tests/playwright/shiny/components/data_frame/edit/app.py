from palmerpenguins import load_penguins_raw  # pyright: ignore[reportMissingTypeStubs]

from shiny import App, Inputs, Outputs, Session, module, render, ui
from shiny.render._dataframe import CellPatch

# TODO-barret-render.data_frame; Make an example that uses a dataframe that then updates a higher level reactive, that causes the df to update... which causes the table to render completely
# TODO-barret-render.data_frame; When "updating" data, try to maintain the scroll, filter info when a new `df` is supplied;

# TODO-future; Can we maintain pre-processed value and use it within editing?
# A: Doesn't seem possible for now

# TODO-karan-test; Data frame with an `Tag` in column
# TODO-karan-test; Data frame with an `TagList` in (another) column
# TODO-karan-test; Data frame with an `MetadataNode` (`HTMLDependency`) in (another) column; Use the `head=` string field to add a script tag that runs some JS. Then expect the JS object to exist in the DOM
# TODO-karan-test; Data frame with an `HTML` in (another) column

# TODO-karan-test; Data frame edit that returns shiny reactive output UI in cell; Add server hook to render something to that cell; Make sure it works when the data frame data is updated and when the data frame is removed.


# TODO-karan-test; Edit a cell in the first row and hit `shift+enter`. It should not submit the change and stay editing the current cell
# TODO-karan-test; Edit a cell in the last row and hit `enter`. It should not submit the change and stay editing the current cell

# TODO-karan-test; Data frame with html content in the first two columns; Edit a cell in the third column and try to hit `shift + tab`. It should not submit the edit in the current cell and stay at the current cell (not moving to the second or first column)
# TODO-karan-test; Data frame with html content in the last two columns; Edit a cell in the third from last column and try to hit `tab`. It should not submit the edit in the current cell and stay at the current cell (not moving to the last two columns)


# Load the dataset
penguins = load_penguins_raw()
df = penguins

df = df.head(5)


# print(ui.p)
# print(ui.p.__json__)

# raise ValueError("Barret testing!")

for i in range(1, 5):
    df.iloc[i, 1] = ui.p(
        ui.HTML(
            ui.tags.strong(
                ui.tags.em(
                    str(
                        df.iloc[i, 1],
                    )
                )
            )
        )
    )

# from shiny.render._data_frame_utils._datagridtable import serialize_numpy_dtypes

# print(serialize_numpy_dtypes(df))


MOD_ID = "testing"


@module.ui
def mod_ui():
    return ui.TagList(
        ui.card(
            ui.fill.as_fill_item(
                ui.output_data_frame("summary_data"),
            ),
            height="400px",
            fillable=True,
        ),
    )


app_ui = ui.page_fillable(
    {"class": "p-3"},
    # ui.markdown(
    #     "**Instructions**: Select one or more countries in the table below to see more information."
    # ),
    mod_ui(MOD_ID),
)


@module.server
def mod_server(input: Inputs, output: Outputs, session: Session):
    @render.data_frame
    def summary_data():
        # return df
        return render.DataGrid(
            df,
            selection_mode="none",
            editable=True,
            # html_columns=(1,),
            # html_columns=(2,),
            html_columns="auto",
        )
        # return render.DataTable(df, selection_mode="none", editable=True)
        # return render.DataGrid(df, selection_mode="rows", editable=True)
        # return render.DataTable(df, selection_mode="rows", editable=True)
        return render.DataGrid(
            df, selection_mode="rows", editable=False, html_columns=[1]
        )
        # return render.DataTable(df, selection_mode="rows", editable=False)

    # from shiny import reactive
    # @reactive.effect
    # def _():
    #     print(summary_data.data())
    #     print(summary_data.data_patched())
    #     print(summary_data.cell_patches())

    # from shiny import reactive

    # @reactive.effect
    # def _():
    #     print(summary_data._type_hints())

    from shinywidgets import render_widget

    @render_widget
    def country_detail_pop():
        import plotly.express as px

        return px.line(
            px.data.gapminder(),
            x="year",
            y="lifeExp",
            color="country",
            title="Population Over Time",
        )

    # x = "<em>Barret</em>"

    # y = "<em>Barret</em>"
    # html_columns = ["y"]

    # z = ui.HTML("<em>Barret</em>")
    # # z is HTML!

    @summary_data.set_patch_fn
    def upgrade_patch(
        *,
        patch: CellPatch,
    ):
        from shinywidgets import output_widget

        if len(summary_data.cell_patches()) == 0:
            return ui.card(output_widget("country_detail_pop"), height="400px")

        import time

        time.sleep(2)
        if len(summary_data.cell_patches()) > 3:
            import random

            from shiny.types import SafeException

            if random.sample([0, 1], 1)[0]:
                raise SafeException("Safe error message!")
            else:
                raise RuntimeError("Barret testing!")

        val = ui.HTML(f"demo_{patch['value']}")
        # return val

        from htmltools import HTMLDependency, TagList

        print(str(len(summary_data.cell_patches())))

        import random

        return TagList(
            HTMLDependency(
                "barret" + "".join(random.choices("0123456789", k=5)),
                version="1",
                head=f"""
                <script>console.log("patching: {val}")</script>
                """,
            ),
            val,
        )

        return ui.HTML(
            f"""
            <script>console.log("patching: {patch['value']}")</script>
            demo_{patch["value"]}
            """
        )

    # @reactive.effect
    # def _():
    #     print(session.id)
    #     print(summary_data.data_patched())
    #     print("patches: ", summary_data.cell_patches())

    if False:
        # Reactive value with current data
        # Make this a reactive calc
        # summary_data.data_selected_rows()

        @summary_data.set_patches_fn
        async def upgrade_patches(
            # data: pd.DataFrame,
            *,
            patches: list[CellPatch],
            # row_index: int,
            # column_id: str,
            # value: str,
        ):

            new_patches: list[CellPatch] = []
            for patch in patches:
                # prev_value = summary_data.data()
                new_patches.append(
                    {
                        "row_index": patch["row_index"],
                        "column_index": patch["column_index"],
                        "value": await summary_data._patch_fn(patch=patch),
                    }
                )
                extra_patch = patch.copy()
                extra_patch["column_index"] = abs(patch["column_index"] - 1)
                new_patches.append(
                    {
                        "row_index": extra_patch["row_index"],
                        "column_index": extra_patch["column_index"],
                        "value": await summary_data._patch_fn(patch=extra_patch),
                    }
                )

            return new_patches


def server(input: Inputs, output: Outputs, session: Session):
    mod_server(MOD_ID)


app = App(app_ui, server, debug=False)
app.sanitize_errors = True
