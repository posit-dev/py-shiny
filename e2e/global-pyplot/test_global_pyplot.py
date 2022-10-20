from conftest import ShinyAppProc, create_example_fixture
from playwright.sync_api import Page, expect
from controls import CheckboxInput, PlotOutput
import re

globalpyplot_app = create_example_fixture("global_pyplot")


def test_global_pyplot(page: Page, globalpyplot_app: ShinyAppProc):
    page.goto(globalpyplot_app.url)

    CheckboxInput(page, "render").expect.to_be_checked()

    plot_sync = PlotOutput(page, "mpl")
    plot_sync.expect.to_be_visible()
    img_src = plot_sync.loc.get_attribute("src")
    assert img_src.startswith("data:image/png;base64,iVBOR")

    plot_async = PlotOutput(page, "mpl_bad")
    plot_async.expect.not_to_be_visible()
    output = page.locator("#mpl_bad")
    expect(output).to_have_class(re.compile(r"\bshiny-output-error"))

    #optional check: Mention in PR if this is obselete
    message = "matplotlib.pyplot cannot be used from an async render function; please use matplotlib's object-oriented interface instead"
    error = output.inner_text()
    assert error == message






