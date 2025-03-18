from playwright.sync_api import Page, expect
from utils.deploy_utils import skip_on_webkit

from shiny.playwright import controller
from shiny.run import ShinyAppProc


@skip_on_webkit
def test_validate_chat_shiny_output(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    TIMEOUT = 30 * 1000

    chat = controller.Chat(page, "chat")
    expect(chat.loc).to_be_visible(timeout=TIMEOUT)

    # Test that ipyleaflet map has rendered
    # (this make sure we can render HTMLDependency()s statically)
    map_loc = page.locator("#map .leaflet-container")
    expect(map_loc).to_be_visible(timeout=TIMEOUT)

    df1 = controller.OutputDataFrame(page, "df1")
    df2 = controller.OutputDataFrame(page, "df2")
    expect(df1.loc).to_be_visible(timeout=TIMEOUT)
    expect(df2.loc).to_be_visible(timeout=TIMEOUT)

    selection = controller.OutputCode(page, "selected_data")
    expect(selection.loc).to_be_visible(timeout=TIMEOUT)

    df1.expect_column_labels(["a", "b"])
    df2.expect_column_labels(["c", "d"])

    expect(selection.loc).to_contain_text("Empty DataFrame")

    df2.select_rows([0])
    expect(selection.loc).to_contain_text("c  d\n0  1  4\n")

    # Test that plotly plot has rendered
    # (this make sure we can render HTMLDependency()s dynamically)
    plot_loc = page.locator("#plot .plotly")
    expect(plot_loc).to_be_visible(timeout=TIMEOUT)
