import asyncio

from shiny import reactive
from shiny.express import input, ui

pinned_stream = ui.MarkdownStream("auto_scroll_stream")
unpinned_stream = ui.MarkdownStream("no_auto_scroll_stream")

# Chunks are gated behind button clicks so the test controls stream pacing.
# This keeps scroll assertions deterministic regardless of machine load.
pinned_queue: asyncio.Queue[str] = asyncio.Queue()
unpinned_queue: asyncio.Queue[str] = asyncio.Queue()

# Each chunk is taller than the 300px card so a missed auto-scroll is
# unambiguous: the container ends up far from the bottom, not a few px off.
FILLER = "\n\n".join(f"Filler paragraph {i} for scroll height." for i in range(12))


def make_chunk(i: int) -> str:
    return f"\n\nCHUNK-{i}-START\n\n{FILLER}\n\nCHUNK-{i}-END\n\n"


def gated_chunks(queue: asyncio.Queue[str]):
    async def gen():
        while True:
            yield await queue.get()

    return gen()


@reactive.effect
@reactive.event(input.next_chunk)
async def _():
    chunk = make_chunk(input.next_chunk())
    await pinned_queue.put(chunk)
    await unpinned_queue.put(chunk)


@reactive.effect
async def _():
    await pinned_stream.stream(gated_chunks(pinned_queue))
    await unpinned_stream.stream(gated_chunks(unpinned_queue))


ui.input_action_button("next_chunk", "Next chunk")

with ui.card(height="300px", class_="mt-3"):
    ui.card_header("Auto-scroll stream (pinned to bottom)")
    pinned_stream.ui()

with ui.card(height="300px", class_="mt-3"):
    ui.card_header("No auto-scroll stream (stays at top)")
    unpinned_stream.ui(auto_scroll=False)
