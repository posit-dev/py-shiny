import pytest
from playwright.sync_api import Page

from shiny._deprecated import ShinyDeprecationWarning
from shiny.playwright import controller
from shiny.run import ShinyAppProc


def test_output_text_verbatim_deprecated(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)

    caption = controller.InputText(page, "caption")

    # `OutputTextVerbatim` is deprecated alongside `ui.output_text_verbatim()`, but both
    # must keep working until they are removed.
    with pytest.warns(ShinyDeprecationWarning, match="`controller.OutputTextVerbatim`"):
        verbatim = controller.OutputTextVerbatim(page, "verbatim")
    with pytest.warns(ShinyDeprecationWarning, match="`controller.OutputTextVerbatim`"):
        verbatim_placeholder = controller.OutputTextVerbatim(
            page, "verbatim_placeholder"
        )

    verbatim.expect_has_placeholder(False)
    verbatim_placeholder.expect_has_placeholder(True)

    verbatim.expect_value("Data summary")
    verbatim_placeholder.expect_value("Data summary")

    new_value = "Updated summary 123"
    caption.set(new_value)

    verbatim.expect_value(new_value)
    verbatim_placeholder.expect_value(new_value)
