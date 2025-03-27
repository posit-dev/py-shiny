# ------------------------------------------------------------------------------------
# A basic Shiny MarkdownStream powered by Anthropic's Claude model with Bedrock.
# To run it, you'll need an AWS Bedrock configuration.
# To get started, follow the instructions at https://aws.amazon.com/bedrock/claude/
# as well as https://github.com/anthropics/anthropic-sdk-python#aws-bedrock
# ------------------------------------------------------------------------------------
from app_utils import load_dotenv
from chatlas import ChatBedrockAnthropic

from shiny import reactive
from shiny.express import ui

# Either explicitly set the AWS environment variables before launching the app, or set
# them in a file named `.env`. The `python-dotenv` package will load `.env` as
# environment variables which can be read by `os.getenv()`.
load_dotenv()
chat_client = ChatBedrockAnthropic(
    model="anthropic.claude-3-sonnet-20240229-v1:0",
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
