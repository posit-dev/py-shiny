# ------------------------------------------------------------------------------------
# A Shiny Chat example showing how to use different language models via chatlas.
# To run it with all the different providers/models, you'll need API keys for each.
# Namely, OPENAI_API_KEY, ANTHROPIC_API_KEY, and GOOGLE_API_KEY.
# To see how to get these keys, see chatlas' reference:
# https://posit-dev.github.io/chatlas/reference/
# ------------------------------------------------------------------------------------

import chatlas as ctl
from app_utils import load_dotenv

from shiny import reactive
from shiny.express import input, ui

load_dotenv()

models = {
    "claude": [
        "claude-3-7-sonnet-latest",
        "claude-3-opus-latest",
        "claude-3-haiku-20240307",
    ],
    "openai": ["gpt-4o-mini", "gpt-4o"],
    "google": ["gemini-2.0-flash"],
}

model_choices: dict[str, dict[str, str]] = {}
for key, value in models.items():
    model_choices[key] = dict(zip(value, value))

ui.page_opts(
    title="Shiny Chat Playground",
    fillable=True,
    fillable_mobile=True,
)

# Sidebar with input controls
with ui.sidebar(position="right"):
    ui.input_select("model", "Model", choices=model_choices)
    ui.input_select(
        "system_actor",
        "Response style",
        choices=["Chuck Norris", "Darth Vader", "Yoda", "Gandalf", "Sherlock Holmes"],
    )
    ui.input_switch("stream", "Stream", value=True)
    ui.input_slider("temperature", "Temperature", min=0, max=2, step=0.1, value=1)
    ui.input_slider("max_tokens", "Max Tokens", min=1, max=4096, step=1, value=100)
    ui.input_action_button("clear", "Clear chat")

# The chat component
chat = ui.Chat(id="chat")
chat.ui(width="100%")


@reactive.calc
def get_model():
    model_params = {
        "system_prompt": (
            "You are a helpful AI assistant. "
            f" Provide answers in the style of {input.system_actor()}."
        ),
        "model": input.model(),
    }

    if input.model() in models["openai"]:
        chat_client = ctl.ChatOpenAI(**model_params)
    elif input.model() in models["claude"]:
        chat_client = ctl.ChatAnthropic(**model_params)
    elif input.model() in models["google"]:
        chat_client = ctl.ChatGoogle(**model_params)
    else:
        raise ValueError(f"Invalid model: {input.model()}")

    return chat_client


@reactive.calc
def chat_params():
    if input.model() in models["google"]:
        return {
            "generation_config": {
                "temperature": input.temperature(),
                "max_output_tokens": input.max_tokens(),
            }
        }
    else:
        return {
            "temperature": input.temperature(),
            "max_tokens": input.max_tokens(),
        }


@chat.on_user_submit
async def handle_user_input(user_input: str):
    if input.stream():
        response = get_model().stream(user_input, kwargs=chat_params())
        await chat.append_message_stream(response)
    else:
        response = get_model().chat(user_input, echo="none", kwargs=chat_params())
        await chat.append_message(response)


@reactive.effect
@reactive.event(input.clear)
def _():
    chat.clear_messages()
