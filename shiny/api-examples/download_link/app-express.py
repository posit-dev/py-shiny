import asyncio
import random
from datetime import date

from shiny.express import render, ui

ui.page_opts(title="Download Examples")

ui.markdown(
    """
    ## Download Examples

    This example demonstrates using `@render.download` in Express mode with different
    styles and options.

    **Note**: Icons in this example use Font Awesome classes. To see icons, ensure your
    app includes Font Awesome or another icon library.
    """
)

ui.markdown("### Simple Downloads (no icons)")


# Simple download button (default)
@render.download(
    filename=lambda: f"simple-{date.today().isoformat()}.csv",
)
async def downloadSimple():
    await asyncio.sleep(0.25)
    yield "one,two,three\n"
    yield "1,2,3\n"


ui.p()


# Simple download link
@render.download(
    filename=lambda: f"simple-link-{date.today().isoformat()}.csv",
    button=False,
    label="Download as simple link",
)
async def downloadSimpleLink():
    await asyncio.sleep(0.25)
    yield "one,two,three\n"
    yield "4,5,6\n"


ui.hr()

ui.markdown("### Downloads with Icons")


# Download as button with icon
@render.download(
    filename=lambda: f"data-button-{date.today().isoformat()}-{random.randint(100, 999)}.csv",
    icon=ui.tags.i(class_="fa fa-download"),
    label="Download Button",
)
async def downloadButton():
    await asyncio.sleep(0.25)
    yield "one,two,three\n"
    yield "1,2,3\n"


ui.p()


# Download as link with icon
@render.download(
    filename=lambda: f"data-link-{date.today().isoformat()}-{random.randint(100, 999)}.csv",
    button=False,
    icon=ui.tags.i(class_="fa fa-file-download"),
    label="Download Link",
)
async def downloadLink():
    await asyncio.sleep(0.25)
    yield "one,two,three\n"
    yield "4,5,6\n"
