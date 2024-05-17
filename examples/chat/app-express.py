from openai import OpenAI

from shiny import reactive
from shiny.express import render, ui

ui.page_opts(fillable=True, fillable_mobile=True)


@render.chat
def chat():
    return render.Chat(
        messages=[{"content": "Hello! How can I help you?", "role": "assistant"}]
    )


client = OpenAI()


@reactive.effect
@reactive.event(chat.user_input)
async def _():
    messages = chat.messages()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        stream=True,
    )
    for chunk in response:
        content = chunk.choices[0].delta.content
        await chat.append_message(
            content, delta=True
        )  # defaults to role is "assistant"
