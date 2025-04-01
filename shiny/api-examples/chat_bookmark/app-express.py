# ------------------------------------------------------------------------------------
# A basic Shiny Chat example powered by OpenAI.
# ------------------------------------------------------------------------------------

import requests
from chatlas import ChatOpenAI, Turn
from chatlas._content import Content
from dotenv import load_dotenv

from shiny import reactive
from shiny.bookmark import BookmarkState
from shiny.express import app_opts, session, ui
from shiny.types import MISSING

with ui.hold():
    load_dotenv()

chat_client = ChatOpenAI(model="gpt-4o-mini")


# Set some Shiny page options
ui.page_opts(
    fillable=True,
    fillable_mobile=True,
)

# Create and display a Shiny chat component
chat = ui.Chat(
    id="chat",
)
chat.ui(messages=["Hello! Would you like to know the weather today?"])


chat.enable_bookmarking(
    chat_client,
    bookmark_on="response",
    # ONLY for ChatExpress.
    # For shiny-core `ui.Chat()``, use the `App(bookmark_store=)` directly
    bookmark_store="url",
)


def get_current_temperature(latitude: float, longitude: float):
    """
    Get the current weather given a latitude and longitude.

    Parameters
    ----------
    latitude
        The latitude of the location.
    longitude
        The longitude of the location.
    """
    lat_lng = f"latitude={latitude}&longitude={longitude}"
    print("lat_lng:", lat_lng)
    url = f"https://api.open-meteo.com/v1/forecast?{lat_lng}&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
    response = requests.get(url)
    json = response.json()
    print("json:", json)
    return json["current"]


with ui.hold():
    chat_client.register_tool(get_current_temperature)

# chat_client.chat("What's the weather like today in Duluth, MN?", echo="all")
# > 👤 User turn:
# >
# > What's the weather like today in Duluth, MN?
# >
# > 🤖 Assistant turn:
# >
# >  # tool request (call_YRma1FOUHVPGHkfylqdHw886)
# >  get_current_temperature(latitude=46.7833, longitude=-92.1062)
# >
# > << 🤖 finish reason: tool_calls >>
# >
# >
# > 👤 User turn:
# >
# >  # tool result (call_YRma1FOUHVPGHkfylqdHw886)
# >  {'time': '2025-02-27T17:45', 'interval': 900, 'temperature_2m': 3.2, 'wind_speed_10m': 21.6}
# >
# > 🤖 Assistant turn:
# >
# > Today in Duluth, MN, the temperature is approximately 3.2°C with a wind speed of 21.6 km/h.


# Generate a response when the user submits a message
@chat.on_user_submit
async def handle_user_input(user_input: str):
    response = await chat_client.stream_async(user_input, echo="all")
    await chat.append_message_stream(response)
