# pyright: reportUnknownMemberType = false
# pyright: reportMissingTypeStubs = false
# pyright: reportArgumentType = false
# pyright: reportUnknownMemberType = false

from palmerpenguins import load_penguins_raw

from shiny import App, Inputs, Outputs, Session, module, render, ui
from shiny.render import CellPatch

# TODO-barret-render.data_frame; Make an example that uses a dataframe that then updates a higher level reactive, that causes the df to update... which causes the table to render completely
# TODO-barret-render.data_frame; When "updating" data, try to maintain the scroll, filter info when a new `df` is supplied;

# TODO-karan-test; Click outside the table. Tab to the column name, hit enter. Verify the table becomes sorted. Tab to an HTML column name, hit enter. Verify the sort does not update.

# TODO-karan-test; Enable rows selection and editable. Select (and verify) a row. Edit a cell content in that row. Verify the row is not focused. Hit escape key. Verify the cell value is not updated. Verify the row is focused. Hit escape key again. Verify the row is not focused. (Possibly verify the container div is focused?)
# TODO-karan-test; Enable rows selection and editable. Select (and verify) a row. Edit a cell content in that row. Click a cell in another row. Verify the new row is selected and focused. Verify the old row is not selected. Verify the old row cell value was updated.
# TODO-karan-test; Enable rows selection and editable. Select (and verify) a row. Hit enter to edit the first cell in that row. Hit escape key. Verify the same row is focused. Scroll right and display an html column in the left part of the view. Hit enter to edit the first visible non-html cell in that row. Verify that cell is editing.

# TODO-future; Can we maintain pre-processed value and use it within editing?
# A: Doesn't seem possible for now

# Load the dataset
penguins = load_penguins_raw()
df = penguins

df = df.head(15)


# Add some HTML content to the dataframe!
df["Sample Number"] = df["Sample Number"].apply(  # pyright: ignore[reportCallIssue]
    lambda x: ui.HTML(  # pyright: ignore[reportUnknownLambdaType]
        str(
            ui.tags.strong(
                ui.tags.em(str(x))  # pyright: ignore[reportUnknownArgumentType]
            )
        )
    )
)


# Use a non-standard index, just in case
df["test_index"] = [
    f"Row {i}" for i in range(0, df.shape[0])
]  # pyright: ignore[reportUnknownArgumentType]
df.set_index("test_index", drop=True, inplace=True)


MOD_ID = "testing"


@module.ui
def mod_ui():
    return ui.TagList(
        ui.card(
            ui.input_text("joe", "Text:"),
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
            selection_mode=("rows"),
            editable=True,
            filters=True,
        )
        # return render.DataTable(df, selection_mode="none", editable=True)
        return render.DataGrid(df, selection_mode="rows", editable=True)
        # return render.DataTable(df, selection_mode="rows", editable=True)
        # return render.DataGrid(df, selection_mode="rows", editable=False)
        # return render.DataTable(df, selection_mode="rows", editable=False)

    from shiny import reactive

    # @reactive.effect
    # def _():
    #     print("Filters:", summary_data.filter())
    # @reactive.effect
    # def _():
    #     print("Sorting:", summary_data.sort())
    # @reactive.effect
    # def _():
    #     print("indices:", summary_data.data_view_rows())
    # @reactive.effect
    # def _():
    #     print("Data View:\n", summary_data.data_view(selected=False))
    # @reactive.effect
    # def _():
    #     print("Data View (selected):\n", summary_data.data_view(selected=True))

    @reactive.effect
    def _():
        print("Cell Selection:", summary_data.cell_selection())

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

    @summary_data.set_patch_fn
    def upgrade_patch(
        *,
        patch: CellPatch,
    ):
        # from shinywidgets import output_widget

        # if len(summary_data.cell_patches()) == 0:
        #     return ui.card(output_widget("country_detail_pop"), height="400px")

        # import time

        # time.sleep(2)
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
