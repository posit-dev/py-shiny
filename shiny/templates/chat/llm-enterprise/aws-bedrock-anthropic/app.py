# ------------------------------------------------------------------------------------
# A basic Shiny Chat powered by Anthropic's Claude model with Bedrock.
# To run it, you'll need an AWS Bedrock configuration.
# To get started, follow the instructions at https://aws.amazon.com/bedrock/claude/
# as well as https://github.com/anthropics/anthropic-sdk-python#aws-bedrock
# ------------------------------------------------------------------------------------
from app_utils import load_dotenv
from chatlas import ChatBedrockAnthropic

from shiny.express import ui

# Either explicitly set the AWS environment variables before launching the app, or set
# them in a file named `.env`. The `python-dotenv` package will load `.env` as
# environment variables which can be read by `os.getenv()`.
load_dotenv()
chat_client = ChatBedrockAnthropic(
    model="anthropic.claude-3-sonnet-20240229-v1:0",
)

# Set some Shiny page options
ui.page_opts(
    title="Hello Anthropic Claude Chat",
    fillable=True,
    fillable_mobile=True,
)

# Create and display empty chat
chat = ui.Chat(id="chat")
chat.ui()

# Store chat state in the url when an "assistant" response occurs
chat.enable_bookmarking(chat_client, bookmark_store="url")


# Define a callback to run when the user submits a message
@chat.on_user_submit
async def handle_user_input(user_input: str):
    response = await chat_client.stream_async(user_input)
    await chat.append_message_stream(response)
