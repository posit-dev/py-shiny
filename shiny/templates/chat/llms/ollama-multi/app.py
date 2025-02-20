# ------------------------------------------------------------------------------------
# Shiny Chat with local models, powered by Ollama
# ------------------------------------------------------------------------------------

# ChatOllama() requires an Ollama model server to be running locally.
# See the docs for more information on how to set up a local Ollama server.
# https://posit-dev.github.io/chatlas/reference/ChatOllama.html
import ollama
from chatlas import ChatOllama

from shiny import reactive, req
from shiny.express import input, render, ui
from shiny.reactive import ExtendedTask

# Get installed models and choose an initial model for the chat
models_all = [m.model for m in ollama.list().models]

# Pick smallest llama3 if available, or default to the most recent model
default_model = models_all[0]
models_all.sort()
if any([x.startswith("llama3") for x in models_all]):
    default_model = [x for x in models_all if x.startswith("llama3")][0]


# Set some Shiny page options
ui.page_opts(
    title="Hello Ollama Chat",
    fillable=True,
    fillable_mobile=True,
)

with ui.sidebar(title="Chat options"):
    ui.input_select(
        "model",
        "Model",
        choices=models_all,
        selected=default_model,
    )
    with ui.div():
        ui.input_slider("temperature", "Creativity", min=0, max=1, value=0.5, step=0.25)
        with ui.help_text(style="text-align: right;"):

            @render.text
            @reactive.event(input.temperature)
            def text_creativity():
                if input.temperature() < 0.25:
                    return "No creativity"
                elif input.temperature() < 0.5:
                    return "Low creativity"
                elif input.temperature() < 0.75:
                    return "Medium creativity"
                elif input.temperature() < 1:
                    return "High creativity"
                else:
                    return "Max creativity"

    ui.input_action_button("edit_last", "Edit last message", disabled=True)
    ui.input_action_button("clear", "Reset chat")


# Create and display a Shiny chat component
chat = ui.Chat(
    id="chat",
    messages=["Hello! How can I help you today?"],
)

chat.ui()

chat_client = reactive.value[ChatOllama](None)


async def cancel_chat_stream(chat: ChatOllama, stream: ExtendedTask):
    if stream is not None and stream.status() == "running":
        # Cancel current stream
        stream.cancel()
        # Tell chat that the message is complete
        stream_id = chat._current_stream_id
        await chat._append_message(
            {
                "type": "assistant",
                "content": "... [cancelled].",
            },
            chunk="end",
            stream_id=stream_id,
        )
        await chat.append_status_message("In-progress response was cancelled.", type="static")


@reactive.effect
@reactive.event(input.model)
async def change_model():
    if chat_client.get() is None:
        client = ChatOllama(model=input.model())
        await chat.append_status_message(
            ui.HTML(f"Using model <code>{input.model()}</code>"), type="static"
        )
    else:
        stream = streaming_task.get()
        await cancel_chat_stream(chat, stream)

        # TODO: Turns are broken when you cancel an in-progress stream
        turns = chat_client.get().get_turns()
        client = ChatOllama(model=input.model(), turns=turns)
        await chat.append_status_message(
            ui.HTML(f"Model switched to <code>{input.model()}</code>"), type="dynamic"
        )

    chat_client.set(client)


streaming_task = reactive.value[ExtendedTask | None](None)


# Generate a response when the user submits a message
@chat.on_user_submit
async def handle_user_input(user_input: str):
    response = chat_client.get().stream(
        user_input, kwargs={"temperature": input.temperature()}
    )
    task = await chat.append_message_stream(response)
    streaming_task.set(task)


@reactive.effect
@reactive.event(input.clear)
async def reset_chat():
    stream = streaming_task.get()
    if not isinstance(stream, ExtendedTask):
        return

    is_streaming = stream.status() == "running"

    if is_streaming:
        await cancel_chat_stream(chat, stream)
    else:
        await chat.clear_messages()
        await chat.append_message("Hello! How can I help you today?")
        chat_client.set(ChatOllama(model=input.model()))
        await chat.append_status_message(ui.HTML(f"Using model <code>{input.model()}</code>"))


@reactive.effect
def toggle_last_message_button():
    task = streaming_task.get()
    if not isinstance(task, ExtendedTask):
        return

    is_streaming = task.status() == "running"
    ui.update_action_button("edit_last", disabled=is_streaming)
    ui.update_action_button(
        "clear", label="Cancel chat" if is_streaming else "Reset chat"
    )


@reactive.effect
@reactive.event(input.edit_last)
async def edit_last_message():
    req(streaming_task.get().status() != "streaming")

    messages = chat.messages()
    req(len(messages) > 1)

    # Find the index of the last user message
    last_user_index = next(
        (i for i, msg in enumerate(messages) if msg["role"] == "user"), None
    )
    if last_user_index is None:
        raise ValueError("No user messages found")

    last_user_msg = messages[last_user_index]["content"]
    messages = messages[:last_user_index]  # Keep only messages before last user message

    # Reset chat UI state prior to last user message
    await chat.clear_messages()
    for message in messages:
        await chat.append_message(message)

    chat.update_user_input(value=last_user_msg, focus=True)
