from palmerpenguins import load_penguins_raw  # pyright: ignore[reportMissingTypeStubs]

from shiny import App, Inputs, Outputs, Session, module, render, ui
from shiny.render._dataframe import CellPatch

# TODO-barret-render.data_frame; Make an example that uses a dataframe that then updates a higher level reactive, that causes the df to update... which causes the table to render completely
# TODO-barret-render.data_frame; When "updating" data, try to maintain the scroll, filter info when a new `df` is supplied;


# Load the dataset
penguins = load_penguins_raw()
df = penguins

df = df.head(5)

for i in range(1, 5):
    df.iloc[i, 1] = ui.tags.strong(ui.tags.em(str(df.iloc[i, 1]))).get_html_string()


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
        return render.DataGrid(df, selection_mode="none", editable=True)
        return render.DataTable(df, selection_mode="none", editable=True)
        # return render.DataGrid(df, selection_mode="rows", editable=True)
        # return render.DataTable(df, selection_mode="rows", editable=True)
        # return render.DataGrid(df, selection_mode="rows", editable=False)
        # return render.DataTable(df, selection_mode="rows", editable=False)

    # from shiny import reactive
    # @reactive.effect
    # def _():
    #     print(summary_data.data())
    #     print(summary_data.data_patched())
    #     print(summary_data.cell_patches())

    @summary_data.set_patch_fn
    async def upgrade_patch(
        *,
        patch: CellPatch,
    ):
        if len(summary_data.cell_patches()) > 3:
            import random

            from shiny.types import SafeException

            if random.sample([0, 1], 1)[0]:
                raise SafeException("Safe error message!")
            else:
                raise RuntimeError("Barret testing!")

        return "demo_" + patch["value"]

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
