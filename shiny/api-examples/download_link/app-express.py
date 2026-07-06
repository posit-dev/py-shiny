import asyncio
import random
from datetime import date

from shiny.express import render, ui
from shiny.ui import download_link

download_link("downloadData", "Download")

# In Express mode, `@render.download` automatically renders a download button. Wrap it
# in `ui.hold()` to suppress the button so the `download_link()` above is used instead.
with ui.hold():

    @render.download(
        filename=lambda: f"data-{date.today().isoformat()}-{random.randint(100, 999)}.csv"
    )
    async def downloadData():
        await asyncio.sleep(0.25)
        yield "one,two,three\n"
        yield "a,1,2\n"
        yield "b,4,5\n"
