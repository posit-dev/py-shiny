import asyncio
import random
from datetime import date

from shiny.express import render


@render.download_link(
    filename=lambda: f"data-{date.today().isoformat()}-{random.randint(100, 999)}.csv"
)
async def downloadData():
    await asyncio.sleep(0.25)
    yield "one,two,three\n"
    yield "a,1,2\n"
    yield "b,4,5\n"
