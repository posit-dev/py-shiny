import asyncio

from shiny import reactive
from shiny.express import input, ui

stream = ui.MarkdownStream("auto_scroll_stream")

# Chunks are gated behind button clicks so the test controls stream pacing.
# This keeps scroll assertions deterministic regardless of machine load.
chunk_queue: asyncio.Queue[str] = asyncio.Queue()

# Each chunk is taller than the 300px card so a missed auto-scroll is
# unambiguous: the container ends up far from the bottom, not a few px off.
FILLER = "\n\n".join(f"Filler paragraph {i} for scroll height." for i in range(12))


def make_chunk(i: int) -> str:
    return f"\n\nCHUNK-{i}-START\n\n{FILLER}\n\nCHUNK-{i}-END\n\n"


async def gated_chunks():
    while True:
        yield await chunk_queue.get()


@reactive.effect
@reactive.event(input.next_chunk)
async def _():
    await chunk_queue.put(make_chunk(input.next_chunk()))


@reactive.effect
async def _():
    await stream.stream(gated_chunks())


ui.input_action_button("next_chunk", "Next chunk")

with ui.card(height="300px", class_="mt-3"):
    ui.card_header("Auto-scroll stream")
    stream.ui()
