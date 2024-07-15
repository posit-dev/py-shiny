from playwright.sync_api import Page
from utils.deploy_utils import skip_if_not_chrome

from shiny.playwright import controller
from shiny.run import ShinyAppProc


@skip_if_not_chrome
def test_patch_exits_saving_state(
    page: Page,
    local_app: ShinyAppProc,
) -> None:
    page.goto(local_app.url)

    my_df = controller.OutputDataFrame(page, "my_df")

    my_df.expect_cell("1", row=0, col=0)
    my_df.expect_cell("4", row=0, col=1)

    my_df.expect_class_state("ready", row=0, col=0)
    my_df.set_cell("test value", row=0, col=1)

    my_df.expect_cell("4", row=0, col=1)
    my_df.expect_cell("a value", row=0, col=0)
    my_df.expect_class_state("success", row=0, col=0)

    my_df.expect_class_state("ready", row=0, col=1)
