import json
from typing import List

import shinyswatch
from dotenv import load_dotenv
from openai import AsyncOpenAI
from pydantic import BaseModel

from shiny import App, reactive, render, ui

load_dotenv()

# Initialize AsyncOpenAI client
client = AsyncOpenAI()


# Define the recipe schema using Pydantic
class Ingredient(BaseModel):
    name: str
    amount: str
    unit: str


class RecipeStep(BaseModel):
    step_number: int
    instruction: str


class Recipe(BaseModel):
    name: str
    description: str
    ingredients: List[Ingredient]
    steps: List[RecipeStep]
    prep_time: str
    cook_time: str
    servings: int


app_ui = ui.page_fillable(
    ui.layout_sidebar(
        ui.sidebar(
            ui.input_action_button("clear", "New Chat"),
            ui.accordion(
                ui.accordion_panel("Recipe Summary", ui.output_ui("recipe_display")),
                ui.accordion_panel("JSON View", ui.output_code("json_view")),
            ),
            id="sidebar",
            open="closed",
            width="500px",
        ),
        ui.chat_ui("chat"),
    ),
    title="Recipe Assistant",
    theme=shinyswatch.theme.minty,
)


def server(input, output, session):
    welcome_message = {
        "content": "Hello! I'm your Recipe Assistant. Ask me about any recipe, and I'll help you find and understand it. When you're ready for a structured summary, just say 'Summarize recipe'.",
        "role": "assistant",
    }
    chat = ui.Chat(id="chat", messages=[welcome_message])
    recipe = reactive.Value(None)

    @chat.on_user_submit
    async def _():
        user_message = chat.messages()[-1]["content"]

        if "summarize recipe" in user_message.lower():
            # Use Structured Outputs to get recipe details
            completion = await client.beta.chat.completions.parse(
                model="gpt-4o-2024-08-06",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful recipe assistant. Provide recipe details based on the previous conversation.",
                    },
                    *chat.messages(format="openai"),
                ],
                response_format=Recipe,
            )

            recipe.set(completion.choices[0].message.parsed)

            await chat.append_message(
                {
                    "role": "assistant",
                    "content": "I've summarized the recipe for you. You can see the structured details and JSON view in the sidebar.",
                }
            )

            ui.update_sidebar("sidebar", show=True)

        else:
            # Continue the conversation normally
            response = await client.chat.completions.create(
                model="gpt-4o-2024-08-06",
                messages=chat.messages(format="openai"),
                stream=True,
            )
            await chat.append_message_stream(response)

    @output
    @render.ui
    def recipe_display():
        if recipe() is None:
            return ui.p("No recipe summary available yet.")

        r = recipe()
        return ui.div(
            ui.h3(r.name),
            ui.p(r.description),
            ui.h4("Ingredients:"),
            ui.tags.ul(
                [
                    ui.tags.li(f"{ing.amount} {ing.unit} {ing.name}")
                    for ing in r.ingredients
                ]
            ),
            ui.h4("Instructions:"),
            ui.tags.ol([ui.tags.li(step.instruction) for step in r.steps]),
            ui.p(f"Prep time: {r.prep_time}"),
            ui.p(f"Cook time: {r.cook_time}"),
            ui.p(f"Servings: {r.servings}"),
            style="border: 1px solid #ccc; padding: 10px; margin-top: 20px;",
        )

    @output
    @render.code
    def json_view():
        if recipe() is None:
            return "No recipe JSON available yet."

        json_str = json.dumps(recipe().dict(), indent=2)
        return json_str

    @reactive.Effect
    @reactive.event(input.clear)
    async def _():
        await chat.clear_messages()
        await chat.append_message(welcome_message)
        recipe.set(None)


app = App(app_ui, server)
