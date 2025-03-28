# ------------------------------------------------------------------------------------
# A basic Shiny MarkdownStream example powered by OpenAI running on Azure.
# ------------------------------------------------------------------------------------
from app_utils import load_dotenv
from chatlas import ChatAzureOpenAI

from shiny import reactive
from shiny.express import ui

# ChatAzureOpenAI() requires an API key from Azure OpenAI.
# See the docs for more information on how to obtain one.
# https://posit-dev.github.io/chatlas/reference/ChatAzureOpenAI.html
load_dotenv()
chat_client = ChatAzureOpenAI(
    endpoint="https://my-endpoint.openai.azure.com",
    deployment_id="gpt-4o-mini",
    api_version="2024-08-01-preview",
)


# Some sidebar input controls to populate a prompt and trigger the stream
with ui.sidebar():
    ui.input_select(
        "comic",
        "Choose a comedian",
        choices=["Jerry Seinfeld", "Ali Wong", "Mitch Hedberg"],
    )
    ui.input_action_button("go", "Tell me a joke", class_="btn-primary")

# Create and display a MarkdownStream()
stream = ui.MarkdownStream(id="my_stream")
stream.ui(
    content="Press the button and I'll tell you a joke.",
)


# Clicking the button triggers the streaming joke generation
@reactive.effect
@reactive.event(input.go)
async def do_joke():
    prompt = f"Pretend you are {input.comic()} and tell me a funny joke."
    response = await chat_client.stream_async(prompt)
    await stream.stream(response)
