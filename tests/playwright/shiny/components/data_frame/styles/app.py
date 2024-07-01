from __future__ import annotations

# pyright: reportMissingTypeStubs = false
import pandas as pd
from palmerpenguins import load_penguins_raw

from shiny import App, Inputs, render, ui
from shiny.render._data_frame_utils._styles import StyleInfo

# Load the dataset
penguins = load_penguins_raw()
df = penguins

df = df.iloc[0:5, 0:6]


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

df_styles: list[StyleInfo] = [
    {
        "location": "body",
        "rows": None,
        "cols": None,
        "style": {"background-color": "lightblue"},
    },
    {
        "location": "body",
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

app_ui = ui.page_fillable(
    {"class": "p-3"},
    ui.markdown(
        "**Instructions**: Edit the cells 3 times. Watch the styles change in the first card."
    ),
    ui.card(
        ui.card_header("Styles Function:"),
        ui.output_data_frame("fn_styles"),
        height="400px",
    ),
    ui.card(
        ui.card_header("Styles List:"),
        ui.output_data_frame("list_styles"),
        height="400px",
    ),
)


def server(input: Inputs):

    @render.data_frame
    def fn_styles():

        counter = 0

        def df_styles_fn(data: pd.DataFrame) -> list[StyleInfo]:
            nonlocal counter
            counter = (counter + 1) % len(df_styles)

            ret: list[StyleInfo] = []
            for style in df_styles:
                style_val = style.get("style", None)
                if style_val is None:
                    continue
                if style_val["background-color"] == "lightblue":
                    continue
                ret.append(style)
                if len(ret) >= counter:
                    break

            return ret

        # NOTE - Styles in GT are greedy!
        # Q: Cell editing should not be allowed as styles would be applied given the original data
        #   * Once GT becomes not greedy, we can unlock this.
        # Styles can be subsetted by looking for the row value
        # return df
        return render.DataTable(
            df,
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
            df,
            selection_mode=("rows"),
            editable=True,
            # filters=True,
            styles=df_styles,
        )


app = App(app_ui, server, debug=False)
