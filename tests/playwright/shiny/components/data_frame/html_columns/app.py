import pkgutil
import random
import string
from typing import Any, cast

import palmerpenguins  # pyright: ignore[reportMissingTypeStubs]
import polars as pl
from htmltools import HTMLDependency

from shiny import App, Inputs, Outputs, Session, render, ui
from shiny.render import CellPatch

pd_penguins = palmerpenguins.load_penguins_raw()
pl_penguins = pl.read_csv(
    cast(
        bytes,
        pkgutil.get_data(
            "palmerpenguins",
            "data/penguins-raw.csv",
        ),
    ),
    null_values="NA",
)


def random_generator():
    return "".join(
        random.choice(string.ascii_letters + string.digits) for _ in range(8)
    )


htmlDep = HTMLDependency(
    f"studyname-0-{random_generator()}",
    version="1",
    head='<script>window.shinytestvalue = "testing"</script>',
)


def make_underlined_html(x: Any) -> ui.HTML:
    return ui.HTML(f"<u>{x}</u>")


def make_heading(y: Any) -> Any:
    return ui.tags.h1(f"{y}")


def make_island_content(z: Any) -> ui.TagList:
    return ui.TagList(
        ui.input_checkbox(f"checkbox_{z}_{random_generator()}", f"{z}"),
        ui.tags.img(
            src="https://dka575ofm4ao0.cloudfront.net/pages-transactional_logos/retina/276517/posit-logo-fullcolor-TM.png",
            height="20%",
            width="20%",
        ),
    )


studyName = pd_penguins["studyName"].copy().astype("object")
# Set the first value of the column to an html object so the column is treated as object by narwhals (not str)
studyName[0] = htmlDep
pd_penguins["studyName"] = studyName
pd_penguins["Species"] = pd_penguins["Species"].apply(make_underlined_html)
pd_penguins["Region"] = pd_penguins["Region"].apply(make_heading)
pd_penguins["Island"] = pd_penguins["Island"].apply(make_island_content)
# Convert column 5 (Stage) to object dtype before assigning HTML objects (required for pandas 3.0+)
pd_penguins["Stage"] = pd_penguins["Stage"].astype("object")

pd_penguins.iloc[0, 5] = cast(Any, ui.div(str(pd_penguins.iloc[0, 5])))
pd_penguins.iloc[1, 5] = cast(
    Any,
    ui.p(
        ui.input_action_button("pandas_test_cell_button", "Test button"),
        ui.output_text_verbatim("pandas_test_cell_text", placeholder=True),
    ),
)


pl_penguins = (
    pl_penguins.replace_column(
        0,
        pl.Series(
            [
                ui.div(htmlDep) if i == 0 else val
                for i, val in enumerate(pl_penguins["studyName"])
            ]
        ).alias("studyName"),
    )
    .replace_column(
        2,  # Species
        pl.Series([ui.tags.u(x) for x in pl_penguins["Species"].to_list()]).alias(
            "Species"
        ),
    )
    .replace_column(
        3,  # Region
        pl.Series([ui.h1(x) for x in pl_penguins["Region"].to_list()]).alias("Region"),
    )
    .replace_column(
        4,  # Island
        pl.Series(
            [
                ui.div(
                    ui.input_checkbox(f"checkbox_{x}_{random_generator()}", f"{x}"),
                    ui.tags.img(
                        src="https://dka575ofm4ao0.cloudfront.net/pages-transactional_logos/retina/276517/posit-logo-fullcolor-TM.png",
                        height="20%",
                        width="20%",
                    ),
                )
                for x in pl_penguins["Island"]
            ],
        ).alias("Island"),
    )
    .replace_column(
        5,  # Stage
        pl.Series(
            [
                (
                    ui.p(
                        ui.input_action_button(
                            "polars_test_cell_button", "Test button"
                        ),
                        ui.output_text_verbatim(
                            "polars_test_cell_text", placeholder=True
                        ),
                    )
                    if i == 1
                    else ui.div(val)
                )
                for i, val in enumerate(pl_penguins["Stage"])
            ]
        ).alias("Stage"),
    )
    .with_columns(pl.col("Sex").replace("NA", ""))
)


app_ui = ui.page_fluid(
    ui.navset_card_underline(
        ui.nav_panel(
            "init",
            "Click another tab to initialize the larger output data frames",
        ),
        ui.nav_panel(
            "pandas",
            ui.output_data_frame("pandas_df"),
        ),
        ui.nav_panel(
            "polars",
            ui.output_data_frame("polars_df"),
        ),
        id="tab",
        selected="pandas",
    )
)


def server(input: Inputs, output: Outputs, session: Session) -> None:

    @render.text
    def pandas_test_cell_text():
        return f"pandas_test_cell_value {input.pandas_test_cell_button()}"

    @render.text
    def polars_test_cell_text():
        return f"polars_test_cell_value {input.polars_test_cell_button()}"

    @render.data_frame
    def pandas_df():
        return render.DataGrid(
            data=pd_penguins,
            filters=True,
            editable=True,
        )

    @render.data_frame
    def polars_df():
        return render.DataGrid(
            data=pl_penguins,
            filters=True,
            editable=True,
        )

    async def upgrade_patch(
        *,
        patch: CellPatch,
    ):
        if patch["column_index"] == 6:  # only for Individual ID
            return f"ID: {patch['value']}"
        else:
            return patch["value"]

    pandas_df.set_patch_fn(upgrade_patch)
    polars_df.set_patch_fn(upgrade_patch)


app = App(app_ui, server)
