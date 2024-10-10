import re

from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc

backends = [
    {
        "name": "pandas",
        "prefix": "pd",
        "df_original": "pd_df_original",
        "selected_row": "selected_pandas_row",
    },
    {
        "name": "narwhals",
        "prefix": "nw",
        "df_original": "nw_df_original",
        "selected_row": "selected_nw_row",
    },
    {
        "name": "pyarrow",
        "prefix": "pa",
        "df_original": "pa_df_original",
        "selected_row": "selected_pa_row",
    },
    {
        "name": "polars",
        "prefix": "pl",
        "df_original": "pl_df_original",
        "selected_row": "selected_pl_row",
    },
    {
        "name": "modin",
        "prefix": "mpd",
        "df_original": "mpd_df_original",
        "selected_row": "selected_mpd_row",
    },
]


def test_data_frame_data_type(
    page: Page,
    local_app: ShinyAppProc,
) -> None:
    page.goto(local_app.url)
    # Iterate over the backends
    for backend in backends:
        # Perform output code tests
        controller.OutputCode(page, f"{backend['prefix']}_type").expect_value(
            re.compile(backend["name"])
        )
        controller.OutputCode(page, f"{backend['prefix']}_data").expect_value(
            re.compile(backend["name"])
        )
        controller.OutputCode(page, f"{backend['prefix']}_data_view").expect_value(
            re.compile(backend["name"])
        )
        controller.OutputCode(
            page, f"{backend['prefix']}_data_view_selected"
        ).expect_value(re.compile(backend["name"]))

        # Perform output dataframe tests
        controller.OutputDataFrame(page, backend["selected_row"]).expect_column_labels(
            ["studyName", "Sample Number"]
        )
        controller.OutputDataFrame(page, backend["df_original"]).select_rows([1])
        controller.OutputDataFrame(page, backend["selected_row"]).expect_nrow(1)
