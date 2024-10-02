# ------------------------------------------------------------------------------------
# A basic Shiny Chat example powered by OpenAI via LangChain.
# To run it, you'll need OpenAI API key.
# To get one, follow the instructions at https://platform.openai.com/docs/quickstart
# To use other providers/models via LangChain, see https://python.langchain.com/v0.1/docs/modules/model_io/chat/quick_start/
# ------------------------------------------------------------------------------------
import os

from app_utils import load_dotenv
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI

from shiny.express import ui

# Set some Shiny page options
ui.page_opts(
    title="Hello LangChain Chat Models",
    fillable=True,
    fillable_mobile=True,
)

# Create and display a Shiny chat component
chat = ui.Chat(
    id="chat",
    messages=["Hello! How can I help you today?"],
)
chat.ui()


# Define a callback to run when the user submits a message
@chat.on_user_submit
async def _(message):
    response = llm.astream(HumanMessage(message))
    await chat.append_message_stream(response)


# Create a LangChain chat model with OpenAI that remembers chat history
#
# Either explicitly set the OPENAI_API_KEY environment variable before launching the
# app, or set them in a file named `.env`. The `python-dotenv` package will load `.env`
# as environment variables which can later be read by `os.getenv()`.
load_dotenv()
model = ChatOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))  # type: ignore

prompt = ChatPromptTemplate.from_messages(
    [
        SystemMessage("You are a helpful assistant."),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

history = InMemoryChatMessageHistory()
llm = RunnableWithMessageHistory(prompt | model, lambda: history)
