import re

from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_data_frame_data_type(
    page: Page,
    local_app: ShinyAppProc,
) -> None:
    page.goto(local_app.url)

    # pandas tests
    controller.OutputCode(page, "pd_type").expect_value(re.compile(r"pandas"))
    controller.OutputCode(page, "pd_data").expect_value(re.compile(r"pandas"))
    controller.OutputCode(page, "pd_data_view").expect_value(re.compile(r"pandas"))
    controller.OutputCode(page, "pd_data_view_selected").expect_value(
        re.compile(r"pandas")
    )
    controller.OutputCode(page, "selected_pandas_row").expect_value(
        re.compile(r"Empty DataFrame")
    )
    controller.OutputDataFrame(page, "pd_df_original").cell_locator(0, 0).click()
    controller.OutputCode(page, "selected_pandas_row").expect_value(
        re.compile(r"PAL0708")
    )

    # narwhals tests
    controller.OutputCode(page, "nw_type").expect_value(re.compile(r"narwhals"))
    controller.OutputCode(page, "nw_data").expect_value(re.compile(r"narwhals"))
    controller.OutputCode(page, "nw_data_view").expect_value(re.compile(r"narwhals"))
    controller.OutputCode(page, "nw_data_view_selected").expect_value(
        re.compile(r"narwhals")
    )
    controller.OutputDataFrame(page, "nw_df_original").cell_locator(0, 0).click()
    controller.OutputCode(page, "selected_nw_row").expect_value(re.compile(r"PAL0708"))

    # pyArrow tests
    controller.OutputCode(page, "pa_type").expect_value(re.compile(r"pyarrow"))
    controller.OutputCode(page, "pa_data").expect_value(re.compile(r"pyarrow"))
    controller.OutputCode(page, "pa_data_view").expect_value(re.compile(r"pyarrow"))
    controller.OutputCode(page, "pa_data_view_selected").expect_value(
        re.compile(r"pyarrow")
    )
    controller.OutputDataFrame(page, "pa_df_original").cell_locator(0, 0).click()
    controller.OutputCode(page, "selected_pa_row").expect_value(re.compile(r"PAL0708"))

    # polars tests
    controller.OutputCode(page, "pl_type").expect_value(re.compile(r"polars"))
    controller.OutputCode(page, "pl_data").expect_value(re.compile(r"polars"))
    controller.OutputCode(page, "pl_data_view").expect_value(re.compile(r"polars"))
    controller.OutputCode(page, "pl_data_view_selected").expect_value(
        re.compile(r"polars")
    )
    controller.OutputDataFrame(page, "pl_df_original").cell_locator(0, 0).click()
    controller.OutputCode(page, "selected_pl_row").expect_value(re.compile(r"PAL0708"))

    # modin tests
    controller.OutputCode(page, "mpd_type").expect_value(re.compile(r"modin"))
    controller.OutputCode(page, "mpd_data").expect_value(re.compile(r"modin"))
    controller.OutputCode(page, "mpd_data_view").expect_value(re.compile(r"modin"))
    controller.OutputCode(page, "mpd_data_view_selected").expect_value(
        re.compile(r"modin")
    )
    controller.OutputDataFrame(page, "mpd_df_original").cell_locator(0, 0).click()
    controller.OutputCode(page, "selected_mpd_row").expect_value(re.compile(r"PAL0708"))
