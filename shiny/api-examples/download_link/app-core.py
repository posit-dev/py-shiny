import asyncio
import random
from datetime import date

from shiny import App, Inputs, Outputs, Session, render, ui

app_ui = ui.page_fluid(
    ui.download_link("downloadData", "Download"),
)


def server(input: Inputs, output: Outputs, session: Session):
    @render.download(
        filename=lambda: f"新型-{date.today().isoformat()}-{random.randint(100, 999)}.csv"
    )
    async def downloadData():
        await asyncio.sleep(0.25)
        yield "one,two,three\n"
        yield "新,1,2\n"
        yield "型,4,5\n"


app = App(app_ui, server)
