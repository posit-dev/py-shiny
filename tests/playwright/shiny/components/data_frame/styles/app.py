from __future__ import annotations

import pkgutil

# pyright: reportMissingTypeStubs = false
import palmerpenguins
import polars as pl
from narwhals.stable.v1.typing import IntoDataFrame

from shiny import App, Inputs, Outputs, Session, module, reactive, render, ui

# Load the dataset


pd_penguins = palmerpenguins.load_penguins_raw().iloc[0:5, 0:6]
pl_penguins = pl.read_csv(
    pkgutil.get_data(  # pyright: ignore[reportArgumentType]
        "palmerpenguins",
        "data/penguins-raw.csv",
    )
)[["studyName", "Sample Number", "Species", "Region", "Island", "Stage"]].head(5)


# import great_tables as gt
# from great_tables_test_utils import gt_styles

# df_gt = (
#     gt.GT(df)
#     .tab_style(
#         [
#             gt.style.fill(color="lightblue"),
#         ],
#         gt.loc.body(),
#     )
#     .tab_style(
#         [
#             gt.style.fill(color="purple"),
#             gt.style.borders(color="green", style="dashed"),
#         ],
#         gt.loc.body("Species", [1, 2]),
#     )
#     .tab_style(
#         gt.style.fill(color="yellow"),
#         gt.loc.body("Region", [2]),
#     )
#     .tab_style(
#         gt.style.fill(color="red"),
#         gt.loc.body("Island"),
#     )
# )
# df_styles = gt_styles(df_gt)

df_styles: list[render.StyleInfo] = [
    {
        "style": {"color": "darkorange", "font-weight": "bold"},
    },
    {
        "rows": None,
        "cols": None,
        "style": {"background-color": "lightblue"},
    },
    {
        "rows": [1, 2],
        "cols": "Species",
        "style": {
            "background-color": "purple",
            "border-color": "green",
            "border-style": "dashed",
        },
    },
    {
        "location": "body",
        "rows": 2,
        "cols": ["Region"],
        "style": {"background-color": "yellow"},
    },
    {
        "location": "body",
        "rows": None,
        "cols": [4],  # "Island",
        "style": {"background-color": "red"},
    },
    {
        "location": "body",
        "rows": [False, True, False, False, False],
        "cols": [False, False, False, False, True, True],  # "Stage",
        "style": {"background-color": "green"},
    },
]


@module.ui
def mod_ui():
    return ui.TagList(
        ui.markdown(
            "**Instructions**: Edit the cells 3 times. Watch the styles change in the first card."
        ),
        ui.card(
            ui.card_header("Styles Function:"),
            ui.output_data_frame("fn_styles"),
        ),
        ui.card(
            ui.card_header("Styles List:"),
            ui.output_data_frame("list_styles"),
        ),
    )


@module.server
def mod_server(
    input: Inputs,
    output: Outputs,
    session: Session,
    data: IntoDataFrame,
):
    @render.data_frame
    def fn_styles():

        def df_styles_fn(
            data: IntoDataFrame,
        ) -> list[render.StyleInfo]:

            def style_is_everywhere(style_info: render.StyleInfo):
                return (style_info.get("rows", None) is None) and (
                    style_info.get("cols", None) is None
                )

            everywhere_styles = [s for s in df_styles if style_is_everywhere(s)]

            with reactive.isolate():
                patch_size = len(fn_styles._cell_patch_map().keys()) + 1
            if patch_size > len(df_styles) - len(everywhere_styles):
                patch_size = 1

            ret: list[render.StyleInfo] = []
            for style_info in df_styles:
                style_val = style_info.get("style", None)
                if style_val is None:
                    continue
                if style_is_everywhere(style_info):
                    continue
                ret.append(style_info)
                if len(ret) >= patch_size:
                    break
            return ret

        # NOTE - Styles in GT are greedy!
        # Q: Cell editing should not be allowed as styles would be applied given the original data
        #   * Once GT becomes not greedy, we can unlock this.
        # Styles can be subsetted by looking for the row value
        # return df
        return render.DataTable(
            data,
            selection_mode=("rows"),
            editable=True,
            # filters=True,
            styles=df_styles_fn,
        )
        # # Ideal
        # return render.DataGrid(
        #     df_gt,
        #     selection_mode=("rows"),
        #     editable=True,
        # )

    @render.data_frame
    def list_styles():
        return render.DataTable(
            data,
            selection_mode=("rows"),
            editable=True,
            # filters=True,
            styles=df_styles,
        )


app_ui = ui.page_fillable(
    ui.navset_underline(
        ui.nav_panel("pandas", mod_ui("pandas")),
        ui.nav_panel("polars", mod_ui("polars")),
        id="tab",
    )
)


def server(input: Inputs):
    mod_server("pandas", pd_penguins)
    mod_server("polars", pl_penguins)


app = App(app_ui, server, debug=False)
