# ------------------------------------------------------------------------------------
# A basic Shiny Chat powered by Anthropic's Claude model with Bedrock.
# To run it, you'll need an AWS Bedrock configuration.
# To get started, follow the instructions at https://aws.amazon.com/bedrock/claude/
# as well as https://github.com/anthropics/anthropic-sdk-python#aws-bedrock
# ------------------------------------------------------------------------------------
from anthropic import AnthropicBedrock

from shiny.express import ui

# Although you can set the AWS credentials here, it's recommended to put them in an .env
# file and load them with `dotenv` so your keys aren't exposed with your code.
# from dotenv import load_dotenv
# load_dotenv()
llm = AnthropicBedrock(
    # aws_secret_key="..."
    # aws_access_key="..."
    # aws_region="..."
    # aws_account_id="..."
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
