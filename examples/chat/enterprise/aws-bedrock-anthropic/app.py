# ------------------------------------------------------------------------------------
# A basic Shiny Chat powered by Anthropic's Claude model with Bedrock.
# To run it, you'll need an AWS Bedrock configuration.
# To get started, follow the instructions at https://aws.amazon.com/bedrock/claude/
# as well as https://github.com/anthropics/anthropic-sdk-python#aws-bedrock
# ------------------------------------------------------------------------------------
from anthropic import AnthropicBedrock

from shiny.express import ui

# In Shiny Core, do `from app_utils import load_dotenv`
from .app_utils import load_dotenv

# Either explicitly set the AWS environment variables before launching the app, or set
# them in a file named `.env`. The `python-dotenv` package will load `.env` as
# environment variables which can be read by `os.getenv()`.
load_dotenv()
llm = AnthropicBedrock(
    # aws_secret_key=os.getenv("AWS_SECRET_KEY"),
    # aws_access_key=os.getenv("AWS_ACCESS_KEY"),
    # aws_region=os.getenv("AWS_REGION"),
    # aws_account_id=os.getenv("AWS_ACCOUNT_ID"),
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


# Define a callback to run when the user submits a message
@chat.on_user_submit
async def _():
    # Get messages currently in the chat
    messages = chat.messages()
    # Create a response message stream
    response = await llm.messages.create(
        model="anthropic.claude-3-sonnet-20240229-v1:0",
        messages=messages,
        stream=True,
        max_tokens=1000,
    )
    # Append the response stream into the chat
    await chat.append_message_stream(response)
