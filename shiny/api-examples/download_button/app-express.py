import asyncio
import random
from datetime import date

from shiny.express import render


@render.download(
    filename=lambda: f"新型-{date.today().isoformat()}-{random.randint(100, 999)}.csv"
)
async def downloadData():
    await asyncio.sleep(0.25)
    yield "one,two,three\n"
    yield "新,1,2\n"
    yield "型,4,5\n"
