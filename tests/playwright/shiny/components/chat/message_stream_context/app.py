import asyncio

from shiny import reactive
from shiny.express import input, render, ui

SLEEP_TIME = 0.25

ui.page_opts(title="Hello chat message streams")

with ui.sidebar(style="height:100%"):
    ui.input_action_button("stream_1", "Stream 1")
    ui.input_action_button("stream_2", "Stream 2")
    ui.input_action_button("stream_3", "Stream 3")
    ui.input_action_button("stream_4", "Stream 4")
    ui.input_action_button("stream_5", "Stream 5")
    ui.input_action_button("stream_6", "Stream 6")

    ui.h6("Message state:", class_="mt-auto mb-0")

    @render.code
    def message_state():
        return str(chat.messages())


chat = ui.Chat(id="chat")
chat.ui()


@chat.on_user_submit
async def _(user_input: str):
    await chat.append_message(f"You said: {user_input}")


@reactive.effect
@reactive.event(input.stream_1)
async def _():
    async with chat.message_stream_context() as msg:
        await msg.append("Basic")
        await asyncio.sleep(SLEEP_TIME)
        await msg.append(" stream")


@reactive.effect
@reactive.event(input.stream_2)
async def _():
    async with chat.message_stream_context() as msg:
        await msg.append("Basic")
        await asyncio.sleep(SLEEP_TIME)
        await msg.append(" stream")
        await asyncio.sleep(SLEEP_TIME)
        await msg.replace("Finished")


@reactive.effect
@reactive.event(input.stream_3)
async def _():
    async with chat.message_stream_context() as outer:
        await outer.append("Outer start")
        await asyncio.sleep(SLEEP_TIME)
        async with chat.message_stream_context() as inner:
            await inner.append("Inner start")
            await asyncio.sleep(SLEEP_TIME)
            await inner.append("Inner end")
        await asyncio.sleep(SLEEP_TIME)
        await outer.append("Outer end")


@reactive.effect
@reactive.event(input.stream_4)
async def _():
    async with chat.message_stream_context() as outer:
        await outer.append("Outer start")
        await asyncio.sleep(SLEEP_TIME)
        async with chat.message_stream_context() as inner:
            await inner.append("Inner start")
            await asyncio.sleep(SLEEP_TIME)
            await inner.replace("Inner end")
        await asyncio.sleep(SLEEP_TIME)
        await outer.append("Outer end")


@reactive.effect
@reactive.event(input.stream_5)
async def _():
    async with chat.message_stream_context() as outer:
        await outer.append("Outer start")
        await asyncio.sleep(SLEEP_TIME)
        await outer.replace("")
        async with chat.message_stream_context() as inner:
            await inner.append("Inner start")
            await asyncio.sleep(SLEEP_TIME)
            await inner.append("Inner end")
        await asyncio.sleep(SLEEP_TIME)
        await outer.append("Outer end")


@reactive.effect
@reactive.event(input.stream_6)
async def _():
    await chat.append_message_stream(outer_stream())


async def outer_stream():
    yield "Outer start"
    await asyncio.sleep(SLEEP_TIME)
    await inner_stream()
    await asyncio.sleep(SLEEP_TIME)
    yield "Outer end"


async def inner_stream():
    async with chat.message_stream_context() as stream:
        await stream.append("Inner start")
        await asyncio.sleep(SLEEP_TIME)
        await stream.append("Inner progress")
        await stream.replace("Inner end")
