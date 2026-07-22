
# Building chatbots with `ui.Chat`

## Overview

`ui.Chat` is a complete conversational UI: a scrolling transcript, a
markdown-rendering message area, and a submit box. You create one `Chat`,
render it, register an `@chat.on_user_submit` callback, and append responses.
Do NOT build a chat out of `input_text_area` + `output_ui` + manual state — the
component handles streaming, markdown, loading indicators, and cancellation for
you.

All response methods are async; write async callbacks and `await` them.

## Minimal app (echo bot)

```python
from shiny.express import ui

ui.page_opts(title="Hello Chat", fillable=True)

chat = ui.Chat(id="chat")
chat.ui(messages=["Hi! Send a message and I'll echo it."])


@chat.on_user_submit
async def handle(user_input: str):
    await chat.append_message(f"You said: {user_input}")
```

In **Shiny Core**, place `ui.chat_ui("chat")` in the UI and create
`chat = ui.Chat(id="chat")` inside `server` — the `id=` must match.

## Stream a response

Prefer streaming: it is more responsive and is the real-world path for LLMs.
`append_message_stream()` takes an (async) iterable of chunks. Each chunk is a
markdown string (or a `{"content": ..., "role": "assistant"}` dict):

```python
import asyncio
from shiny.express import ui

chat = ui.Chat(id="chat")
chat.ui()


@chat.on_user_submit
async def handle(user_input: str):
    async def response():
        for word in ["Thinking", " ", "about", " ", user_input]:
            yield word
            await asyncio.sleep(0.1)

    await chat.append_message_stream(response())
```

## Connect an LLM provider

Any provider works; [chatlas](https://posit-dev.github.io/chatlas/) is the
recommended wrapper. Passing `client=` auto-wires an `on_user_submit` handler
that streams the reply and tracks conversation history for you — no callback
needed:

```python
import os
from chatlas import ChatOpenAI
from shiny.express import ui

chat_client = ChatOpenAI(
    api_key=os.environ["OPENAI_API_KEY"],
    model="gpt-4o",
    system_prompt="You are a helpful assistant.",
)

ui.page_opts(title="Assistant", fillable=True)
chat = ui.Chat(id="chat", client=chat_client)
chat.ui()
```

Swap `ChatOpenAI` for `ChatAnthropic`, `ChatGoogle`, `ChatOllama`, etc. To keep
control of the callback (custom logic, non-chatlas provider), omit `client=` and
stream manually — `stream_async()` returns an async iterable:

```python
@chat.on_user_submit
async def handle(user_input: str):
    response = await chat_client.stream_async(user_input)
    await chat.append_message_stream(response)
```

## Seed and read message history

- **Startup messages:** pass `messages=` to `chat.ui(...)` (Express) or
  `ui.chat_ui(...)` (Core). Use `greeting=` for a welcome shown before any
  conversation.
- **Read the transcript reactively:** `chat.messages()` returns a tuple of
  `{"content", "role"}` dicts, oldest first (last item is the newest user
  message). Call it inside a reactive context / callback:

```python
@chat.on_user_submit
async def handle(user_input: str):
    history = chat.messages()  # e.g. feed to a provider that needs full context
    await chat.append_message_stream(my_model(history))
```

With `client=`, chatlas keeps its own history — you rarely need `messages()`.

## Guardrails and markdown

Transform or validate user input **inside** `on_user_submit` before sending it
to the model (the old `transform_user_input` hook was removed):

```python
@chat.on_user_submit
async def handle(user_input: str):
    if "forbidden" in user_input.lower():
        await chat.append_message("Sorry, I can't help with that.")
        return
    await chat.append_message_stream(chat_client.stream_async(user_input))
```

Response strings are rendered as **markdown** automatically. To insert raw HTML
verbatim (skip markdown), wrap it: `await chat.append_message(ui.HTML(html))`.

For streaming markdown *outside* a chat (e.g. a report that types out), use the
separate `ui.MarkdownStream` / `ui.output_markdown_stream` component instead.

## Quick reference

| Need | API |
|---|---|
| Create chat | `ui.Chat(id, client=None, greeting=None)` |
| Render (Express / Core) | `chat.ui(messages=..., greeting=...)` / `ui.chat_ui(id, ...)` |
| Handle submissions | `@chat.on_user_submit` (callback takes `user_input: str`, optional `attachments`) |
| Append full message | `await chat.append_message(msg)` |
| Stream a message | `await chat.append_message_stream(async_iterable)` |
| Read transcript | `chat.messages()` (reactive) |
| Latest user input | `chat.user_input()` |
| Prefill / submit input box | `chat.update_user_input(value=..., submit=True)` |
| Clear transcript | `await chat.clear_messages()` |
| File uploads | `chat.ui(allow_attachments=True)` -> handler's 2nd arg |
| Bookmark state | `chat.enable_bookmarking(chat_client, bookmark_store="url")` |

## Common mistakes

- Core `id=` on `ui.Chat` not matching `ui.chat_ui("...")` -> chat never wires
  up. They must be identical.
- Using `append_message()` for a streamed/generator response -> use
  `append_message_stream()`; reserve `append_message()` for a complete string.
- Sync callback or forgetting `await` -> responses never appear. Callbacks are
  async and every append/stream call must be awaited.
- Passing `messages=` to `ui.Chat(...)` -> deprecated; pass it to `chat.ui(...)`.
- Expecting `client=` and a manual `on_user_submit` to conflict -> they don't;
  your handler runs *in addition* to the auto-wired streaming handler.
- Reaching for `transform_user_input` / `transform_assistant_response` -> both
  are removed/deprecated; transform input in the callback and post-process
  response strings before appending.
