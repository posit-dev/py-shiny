import pandas as pd
from palmerpenguins import load_penguins_raw  # pyright: ignore[reportMissingTypeStubs]

from shiny import App, Inputs, Outputs, Session, module, reactive, render, ui
from shiny.render._dataframe import CellUpdateInfo

# TODO-barret; Make an example that uses a dataframe that then updates a higher level reactive, that causes the df to update... which causes the table to render completely
# TODO-barret-future; When "updating" data, try to maintain the scroll, filter info when a new `df` is supplied;


# Load the dataset
penguins = load_penguins_raw()

df1 = pd.DataFrame(data={"a": [1, 2]})
df1.insert(1, "a", [3, 4], True)  # pyright: ignore

df = penguins
# df = df1


# df = reactive.value(df1)df = reactive.value(load_penguins_raw())

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
        return render.DataGrid(df, mode="edit")
        return render.DataTable(df, mode="edit")

    @summary_data.set_cell_update_fn
    async def handle_edit(
        *,
        info: CellUpdateInfo,
    ):
        return "demo_" + info["value"]

    @reactive.effect
    def _():
        print(session.id)
        print(summary_data.data_patched())
        print("patches: ", summary_data.cell_patches())

    # summary_data.data_patched()  # ~ patched_df()

    if False:
        # Reactive value with current data
        # Make this a reactive calc
        # summary_data.data_selected_rows()

        from typing import TypedDict

        class CellUpdate(TypedDict):
            row_index: int
            column_id: str
            value: str
            prev: str

        @summary_data.on_cells_update
        async def handle_edit_full(
            # data: pd.DataFrame,
            *,
            cell_changes: list[CellUpdate],
            # row_index: int,
            # column_id: str,
            # value: str,
            # prev: str,
        ):
            data_local = summary_data.data_patched()
            for change in cell_changes:  # typing: ignore
                row_index = change["row_index"]
                column_id = change["column_id"]
                value = change["value"]
                data_local.iat[row_index, column_id] = value
            return data_local

            # _df_patched.set(None)
            # _df_patched.set(new_val)

        # # Handle multiple cells changed at once (like a paste)
        # @summary_data.on_cells_update
        # async def handle_edit(
        #     data: pd.DataFrame,
        #     *,
        #     cell_changes: list[dict],
        # ):

        #     ...

        @summary_data.on_cell_update
        async def handle_edit_simple(
            data: pd.DataFrame,
            *,
            row_index: int,
            column_id: str,
            value: str,
            prev: str,
        ):
            return "formatted_" + value

            # pandas CoW (copy-on-write) an issue?
            # https://pandas.pydata.org/docs/dev/user_guide/copy_on_write.html

            print("edit!", row_index, column_id, value, prev)

            df_local = df.get()
            df_local.iat[row_index, column_id] = value
            df.set(df_local)

            # df.update(lambda x: x.iat[row_index, column_id] = value)
            # df().iat[row_index, column_id] = value

            return
            # # df
            # df_copy = df.copy()
            # df_copy.iat[edit["row"], edit["col"]] = edit["new_value"]
            # return df_copy


def server(input: Inputs, output: Outputs, session: Session):
    mod_server(MOD_ID)


app = App(app_ui, server, debug=False)
app.sanitize_errors = True
