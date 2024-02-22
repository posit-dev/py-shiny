import pandas as pd
from palmerpenguins import load_penguins_raw  # pyright: ignore[reportMissingTypeStubs]

from shiny import App, Inputs, reactive, render, req, ui

# Load the dataset
df = reactive.value(load_penguins_raw())


app_ui = ui.page_fillable(
    {"class": "p-3"},
    # ui.markdown(
    #     "**Instructions**: Select one or more countries in the table below to see more information."
    # ),
    ui.card(
        ui.output_data_frame("summary_data"),
        height="400px",
    ),
    ui.pre(id="barret"),
    ui.tags.script(
        """
        // const window_console_log = console.log;
        // console.log = function() {
        //     window_console_log.apply(console, arguments);
        //     let txt = "log - " + Date.now() + ": ";
        //     for (let i = 0; i < arguments.length; i++) {
        //         if (i > 0) txt += ", ";
        //         txt += arguments[i];
        //     }
        //     $("#barret").append(txt + "\\n");
        // };
        const window_console_error = console.error;
        console.error = function() {
            window_console_error.apply(console, arguments);
            let txt = "error - " + Date.now() + ": ";
            for (let i = 0; i < arguments.length; i++) {
                if (i > 0) txt += ", ";
                txt += arguments[i];
            }
            $("#barret").append(txt + "\\n");
        };
        // console.log("Hello, World!");
        // console.error("Hello, World!");
        """
    ),
)


def server(input: Inputs):
    @render.data_frame
    def summary_data():
        # return df
        return render.DataGrid(df(), row_selection_mode="none", editable=True)
        # return render.DataTable(df, row_selection_mode="multiple")

    @reactive.calc
    def patched_df() -> pd.DataFrame:
        df_local = df.get()
        # apply patch here!

        return df_local

    @summary_data.on_cell_update
    async def handle_edit(
        # Drop this param for now!
        data: pd.DataFrame,
        *,
        row_index: int,
        column_id: str,
        value: str,
        prev: str,
    ):
        # The return value should be coerced by pandas to the correct type
        return "formatted_" + value

    if False:
        # Reactive value with current data
        # Make this a reactive calc
        summary_data.data_patched()  # ~ patched_df()
        # summary_data.data_selected_rows()

        # @summary_data.on_cell_update_method
        # async def handle_edit(
        #     data: pd.DataFrame,
        #     *,
        #     row_index: int,
        #     column_id: str,
        #     value: str,
        #     prev: str,
        # ):
        #     # summary_data.update_cell(row_index, column_id, value)
        #     for updated_cell_info in
        #     return

        @summary_data.on_cell_update_full
        async def handle_edit(
            # data: pd.DataFrame,
            *,
            cell_changes: list[dict],
            # row_index: int,
            # column_id: str,
            # value: str,
            # prev: str,
        ):
            data_local = summary_data.data_patched()
            for change in cell_changes:
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
        async def handle_edit(
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
            return df_copy


app = App(app_ui, server)
