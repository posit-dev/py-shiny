---
name: markdown-streaming
description: Covers streaming Markdown/LLM output into a non-chat UI region in Shiny for Python with `ui.MarkdownStream` - rendering the target, pushing an (async) generator with `.stream()`, choosing markdown/html/text content, and replacing vs. appending. Use when progressively revealing a generated report, summary, or LLM response token-by-token into a card or page area that is NOT a conversation, streaming any incremental text into an output region, or when tempted to repeatedly overwrite an `output_text`/`render.ui` on a timer to fake streaming. For a full chatbot conversation (transcript + submit box) use the `chat` skill and `ui.Chat` instead.
---

# Streaming Markdown with `ui.MarkdownStream`

## Overview

`ui.MarkdownStream` renders a single region that incrementally displays Markdown
(or HTML/plain text) as it arrives — ideal for an LLM-generated report, summary,
or any text you want to reveal token-by-token. It is NOT a chat: there is no
transcript, no user submit box, no message roles. Create one `MarkdownStream`,
render it, and feed it an async generator via `.stream()`.

Do NOT fake streaming by calling `render.text`/`render.ui` repeatedly on a timer
or rebuilding the full string on every reactive tick — `.stream()` handles
incremental rendering, Markdown parsing, and auto-scroll for you.

`.stream()` is async; write async generators and `await` the call.

## Express: stream into a card

```python
import asyncio
from shiny import reactive
from shiny.express import ui

md = ui.MarkdownStream("summary")

with ui.card(height="400px"):
    ui.card_header("Generated summary")
    md.ui(content="Click generate to begin.")


@reactive.effect
async def _():
    async def gen():
        for word in "# Report\n\nStreaming **markdown** word by word.".split(" "):
            yield word + " "
            await asyncio.sleep(0.05)

    await md.stream(gen())
```

## Core: `output_markdown_stream`

In Shiny Core, place `ui.output_markdown_stream(id)` in the UI and create the
`MarkdownStream` with the **same id** in `server`:

```python
import asyncio
from shiny import App, reactive, ui

app_ui = ui.page_fluid(
    ui.card(ui.output_markdown_stream("summary"), height="400px"),
)


def server(input, output, session):
    md = ui.MarkdownStream("summary")

    @reactive.effect
    async def _():
        async def gen():
            for chunk in ["Hello", " ", "**world**"]:
                yield chunk
                await asyncio.sleep(0.1)

        await md.stream(gen())


app = App(app_ui, server)
```

## Stream an LLM response

Any provider that yields chunks works. Wrap its stream in an async generator
that yields Markdown strings (trigger it from a button with `@reactive.event`):

```python
from chatlas import ChatOpenAI
from shiny import reactive
from shiny.express import input, ui

client = ChatOpenAI(system_prompt="Write a short report.")

ui.input_action_button("go", "Generate", class_="btn-primary")
md = ui.MarkdownStream("report")
md.ui(content="Press Generate.")


@reactive.effect
@reactive.event(input.go)
async def _():
    await md.stream(client.stream_async("Summarize today's sales."))
```

`chatlas`'s `stream_async()` already yields text chunks. For a raw SDK, adapt it:
`async for part in resp: yield part.content`.

## Set, replace, and append content

- **Set complete content** (no streaming): pass a one-item list —
  `await md.stream(["# Done\n\nAll finished."])`.
- **Replace** (default): `.stream(gen())` clears existing content first
  (`clear=True`).
- **Append** to what is already shown: `.stream(gen(), clear=False)`.
- **Clear** the region: `await md.clear()`.

## Content type

Content is parsed as **Markdown** (CommonMark) by default. To render raw HTML or
avoid parsing entirely, set `content_type` on the render call:

```python
md.ui(content_type="html")                 # Express
ui.output_markdown_stream("x", content_type="text")  # Core
```

## Quick reference

| Need | API |
|---|---|
| Create stream | `ui.MarkdownStream(id, on_error="auto")` |
| Render (Express) | `md.ui(content="", content_type="markdown", auto_scroll=True, width=..., height=...)` |
| Render (Core) | `ui.output_markdown_stream(id, content=..., content_type=..., ...)` |
| Stream chunks | `await md.stream(async_iterable, clear=True)` |
| Append instead of replace | `await md.stream(gen(), clear=False)` |
| Set full string at once | `await md.stream([content])` |
| Clear region | `await md.clear()` |
| Final streamed value | `task = await md.stream(...)`; `task.result()` (in a reactive context) |
| Content types | `"markdown"` (default), `"html"`, `"text"` |

## Common mistakes

- Core `id` on `ui.MarkdownStream` not matching `ui.output_markdown_stream("...")`
  -> nothing renders. They must be identical.
- Sync function or forgetting `await` on `.stream()` -> content never appears.
  The generator may be sync or async, but `.stream()` itself must be awaited.
- Rebuilding the whole string and re-yielding it each tick -> yield only the new
  chunk; `MarkdownStream` accumulates them.
- Using it for a back-and-forth conversation -> that is `ui.Chat` (see the
  `chat` skill). `MarkdownStream` has no message history or input box.
- Passing UI/output bindings as `content_type="text"` -> they render as literal
  text; use `"markdown"` or `"html"` for embedded UI.
