from __future__ import annotations

import pkgutil

# pyright: reportUnknownMemberType = false
# pyright: reportMissingTypeStubs = false
# pyright: reportArgumentType = false
# pyright: reportUnknownMemberType = false
#
# TODO-barret-render.data_frame; Make an example that uses a dataframe that then updates a higher level reactive, that causes the df to update... which causes the table to render completely
# TODO-barret-render.data_frame; When "updating" data, try to maintain the scroll, filter info when a new `df` is supplied;
#
# TODO-karan-test; Click outside the table. Tab to the column name, hit enter. Verify the table becomes sorted. Tab to an HTML column name, hit enter. Verify the sort does not update.
#
# TODO-future; Can we maintain pre-processed value and use it within editing?
# A: Doesn't seem possible for now
import great_tables as gt
import palmerpenguins  # pyright: ignore[reportMissingTypeStubs]
import polars as pl

from shiny import App, Inputs, Outputs, Session, module, reactive, render, req, ui
from shiny.render import CellPatch
from shiny.render._data_frame_utils._styles import StyleInfo
from shiny.types import Jsonifiable

pd_penguins = palmerpenguins.load_penguins_raw()
pl_penguins = pl.read_csv(
    pkgutil.get_data("palmerpenguins", "data/penguins-raw.csv"),
    null_values="NA",
)

pd_asdf = render.DataTable(pd_penguins)
pl_asdf = render.DataTable(pl_penguins)

# Load the dataset
df = pd_penguins

df = df.head(15)


# Add some HTML content to the dataframe!
df = df.astype({"Sample Number": "object"})
# df.loc[:, "Sample Number"] = df.loc[:, "Sample Number"].astype("object")
df.loc[:, "Sample Number"] = df.loc[
    :, "Sample Number"
].apply(  # pyright: ignore[reportCallIssue]
    lambda x: ui.HTML(  # pyright: ignore[reportUnknownLambdaType]
        str(
            ui.tags.strong(
                ui.tags.em(str(x))  # pyright: ignore[reportUnknownArgumentType]
            )
        )
    )
)


# Use a non-standard index, just in case
df.loc[:, "test_index"] = [
    f"Row {i}" for i in range(0, df.shape[0])
]  # pyright: ignore[reportUnknownArgumentType]
df.set_index("test_index", drop=True, inplace=True)


# print(p)
df = pl_penguins.head(15).with_columns(
    (pl.Series([ui.tags.strong(ui.tags.em(str(x))) for x in range(0, 15)])).alias(
        "Sample Number"
    )
)


print(df)


def gt_style_str_to_obj(style_str: str) -> dict[str, Jsonifiable]:
    # Could use BeautifulSoup here, but this is a simple example
    style_obj: dict[str, Jsonifiable] = {}
    for style_part in style_str.split(";"):
        style_part = style_part.strip()
        if not style_part:
            continue
        key, value = style_part.split(":")
        style_obj[key] = value
    return style_obj


def gt_styles(df_gt: gt.GT) -> list[StyleInfo]:
    styles = df_gt._styles
    ret: list[StyleInfo] = []
    for style in styles:
        location = style.locname
        location = (
            "body"
            if location == "data"  # pyright: ignore[reportUnnecessaryComparison]
            else location
        )
        assert location == "body", f"`style.locname` is {location}, expected 'body'"
        rows = style.rownum
        assert rows is not None
        cols = style.colnum
        if cols is None:
            cols = style.colname
        assert cols is not None

        style_obj: dict[str, Jsonifiable] = {}
        for style_str in style.styles:
            style_obj.update(
                gt_style_str_to_obj(style_str._to_html_style()),
            )
        ret.append(
            {
                "location": location,
                "rows": rows,
                "cols": cols,
                "style": style_obj,
            }
        )
    return ret


# import numpy as np
# import pandas as pd

# np.random.seed(0)
# df2 = pd.DataFrame(np.random.randn(10, 4), columns=["A", "B", "C", "D"])
# df2.style

# df = df2.style
# print(df, dir(df))


MOD_ID = "testing"


@module.ui
def mod_ui():
    return ui.TagList(
        ui.card(
            ui.output_data_frame("selected_summary_data"),
            ui.output_data_frame("summary_data"),
            height="400px",
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
    def selected_summary_data():
        return summary_data.data_view(selected=True)

    @reactive.effect
    async def _():
        req(summary_data.data_view_rows())
        await summary_data.update_cell_selection(
            {
                "type": "row",
                "rows": [0, 2],
            }
        )

    @render.data_frame
    def summary_data():

        df_gt = (
            gt.GT(df)
            .tab_style(
                [
                    gt.style.fill(color="purple"),
                    gt.style.borders(color="green", style="dashed"),
                ],
                gt.loc.body("Species", [1, 2]),
            )
            .tab_style(
                gt.style.fill(color="yellow"),
                gt.loc.body("Region", [2]),
            )
            .tab_style(
                gt.style.fill(color="red"),
                gt.loc.body("Island"),
            )
        )
        df_styles = gt_styles(df_gt)
        counter = 0

        import pandas as pd

        def df_styles_fn(data: pd.DataFrame) -> list[StyleInfo]:
            nonlocal counter
            counter = counter + 2
            if counter > 5:
                counter = 0

            ret: list[StyleInfo] = []
            while len(ret) < counter and len(ret) < len(df_styles):
                ret.append(df_styles[len(ret)])

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
        # Ideal
        return render.DataGrid(
            df_gt,
            # selection_mode=("rows"),
            # editable=True,
            filters=True,
        )
        # return render.DataTable(df, selection_mode="none", editable=True)
        return render.DataGrid(df, selection_mode="rows", editable=True)
        # return render.DataTable(df, selection_mode="rows", editable=True)
        # return render.DataGrid(df, selection_mode="rows", editable=False)
        # return render.DataTable(df, selection_mode="rows", editable=False)

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
    # @reactive.effect
    # def _():
    #     print("Cell Selection:", summary_data.cell_selection())
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

    # from shiny import reactive

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

        # print(str(len(summary_data.cell_patches())))
        import random

        from htmltools import HTMLDependency, TagList

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
