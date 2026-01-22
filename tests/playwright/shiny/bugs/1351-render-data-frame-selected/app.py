import pandas as pd

from shiny import App, Inputs, reactive, render, ui

app_ui = ui.page_fluid(
    ui.markdown(
        """
    ## Description

    When you add a row, click on it and click the clear button you get:


    """
    ),
    ui.input_action_button("add_row", "Add row"),
    ui.input_action_button("clear_table", "Clear table"),
    ui.output_text_verbatim("number_of_selected_rows"),
    ui.output_data_frame("df1"),
)


def server(input: Inputs):
    df = reactive.Value(pd.DataFrame(columns=["A", "B"]))

    @render.data_frame
    def df1():
        return render.DataGrid(df(), selection_mode="rows")

    @reactive.effect
    @reactive.event(input.add_row)
    def _():
        old_df = df()
        new_df = pd.concat(  # pyright: ignore[reportUnknownMemberType]
            [old_df, pd.DataFrame([[1, 2]], columns=["A", "B"])]
        )
        df.set(new_df)

    @render.text
    def number_of_selected_rows():
        df_selected = df1.data_view(selected=True)
        return f"Selected rows: {len(df_selected)}"

    @reactive.effect
    @reactive.event(input.clear_table)
    def _():
        df.set(pd.DataFrame(columns=["A", "B"]))


app = App(app_ui, server)
