import pandas as pd
import seaborn as sns
import shinyswatch

from shiny import App, Inputs, Outputs, Session, reactive, render, req, ui


def app_ui(req):
    dark = True if "dark" in req.query_params else None

    return ui.page_fluid(
        ui.head_content(
            ui.tags.meta(name="viewport", content="width=device-width, initial-scale=1")
        ),
        light_dark_switcher(dark),
        ui.input_select("dataset", "Dataset", sns.get_dataset_names()),
        ui.input_select(
            "selection_mode",
            "Selection mode",
            {
                "none": "(None)",
                "row": "Single row",
                "rows": "Multiple rows",
            },
            selected="rows",
        ),
        ui.input_switch("editable", "Edit", False),
        ui.input_switch("filters", "Filters", True),
        ui.input_switch("gridstyle", "Grid", True),
        ui.input_switch("fullwidth", "Take full width", True),
        ui.output_data_frame("grid"),
        ui.panel_fixed(
            ui.output_code("detail"),
            right="10px",
            bottom="10px",
        ),
        theme=shinyswatch.theme.darkly if dark else None,
        class_="p-3",
    )


def light_dark_switcher(dark):
    return (
        ui.div(
            ui.a(
                {"class": "btn-primary" if not dark else "btn-outline-primary"},
                "Light",
                href="?" if dark else None,
                class_="btn",
            ),
            ui.a(
                {"class": "btn-primary" if dark else "btn-outline-primary"},
                "Dark",
                href="?dark=1" if not dark else None,
                class_="btn",
            ),
            class_="float-end btn-group",
        ),
    )


def server(input: Inputs, output: Outputs, session: Session):
    df: reactive.value[pd.DataFrame] = reactive.value()

    @reactive.effect
    def update_df():
        return df.set(sns.load_dataset(req(input.dataset())))

    @render.data_frame
    def grid():
        height = 350
        width = "100%" if input.fullwidth() else "fit-content"
        if input.gridstyle():
            return render.DataGrid(
                df(),
                width=width,
                height=height,
                filters=input.filters(),
                editable=input.editable(),
                selection_mode=input.selection_mode(),
            )
        else:
            return render.DataTable(
                df(),
                width=width,
                height=height,
                filters=input.filters(),
                editable=input.editable(),
                selection_mode=input.selection_mode(),
            )

    @reactive.effect
    @reactive.event(input.grid_cell_edit)
    def handle_edit():
        edit = input.grid_cell_edit()
        df_copy = df().copy()
        df_copy.iat[edit["row"], edit["col"]] = edit["new_value"]
        df.set(df_copy)

    @render.code
    def detail():
        selected_rows = grid.cell_selection()["rows"]
        if len(selected_rows) > 0:
            return df().iloc[list(selected_rows)]


app = App(app_ui, server)
