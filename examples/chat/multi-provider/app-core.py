from anthropic import Anthropic
from google.generativeai import GenerationConfig, GenerativeModel
from openai import OpenAI

from shiny import App, reactive, render, ui

models = {
    "openai": ["gpt-4o", "gpt-3.5-turbo"],
    "claude": [
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307",
    ],
    "google": ["gemini-1.5-pro-latest"],
    # "huggingface": ["gpt2", "gpt2-medium"],
}

model_choices = {}
for key, value in models.items():
    model_choices[key] = dict(zip(value, value))


app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_select("model", "Model", choices=model_choices),
        ui.input_text_area(
            "system_prompt",
            "System Prompt",
            value="Provide answers in the style of Chuck Norris.",
        ),
        ui.input_switch("stream", "Stream", value=True),
        ui.input_slider("temperature", "Temperature", min=0, max=2, step=0.1, value=1),
        ui.input_slider("max_tokens", "Max Tokens", min=1, max=4096, step=1, value=100),
        position="right",
    ),
    ui.output_chat("chat"),
    title="Shiny Chat Playground",
    fillable=True,
    fillable_mobile=True,
)


def server(input):

    @render.chat
    def chat():
        return render.Chat()

    @reactive.calc
    def client():
        if input.model() in models["openai"]:
            return OpenAI()
        elif input.model() in models["claude"]:
            return Anthropic()
        elif input.model() in models["google"]:
            return GenerativeModel(
                input.model(),
                system_instruction=input.system_prompt(),
            )
        else:
            raise ValueError(f"Invalid model: {input.model()}")

    @reactive.calc
    def create_response():
        c = client()
        if isinstance(c, OpenAI):
            return c.chat.completions.create(
                model=input.model(),
                messages=(
                    {"content": input.system_prompt(), "role": "system"},
                    *chat.messages(),
                ),
                stream=input.stream(),
                temperature=input.temperature(),
                max_tokens=input.max_tokens(),
            )
        elif isinstance(c, Anthropic):
            return c.messages.create(
                model=input.model(),
                messages=chat.messages(),
                stream=input.stream(),
                temperature=input.temperature(),
                max_tokens=input.max_tokens(),
                system=input.system_prompt(),
            )
        elif isinstance(c, GenerativeModel):
            # Change content key to parts
            messages = chat.messages()

            # Convert messages to the format expected by Google's API
            # TODO: we could automatically do this if client is provided?
            contents = [
                {
                    "role": "model" if x["role"] == "assistant" else x["role"],
                    "parts": x["content"],
                }
                for x in messages
            ]

            return c.generate_content(
                contents=contents,
                stream=input.stream(),
                generation_config=GenerationConfig(
                    temperature=input.temperature(),
                    max_output_tokens=input.max_tokens(),
                ),
            )

    @reactive.effect
    @reactive.event(chat.user_input)
    async def _():
        try:
            response = create_response()

            if input.stream():
                await chat.append_message_stream(response)
            else:
                await chat.append_message(response)  # defaults to role is "assistant"

        except Exception as e:
            ui.notification_show(
                [
                    ui.h4("Error generating response"),
                    ui.p(str(e)),
                ],
                type="danger",
                duration=999999,
            )
            raise e


app = App(app_ui, server)
