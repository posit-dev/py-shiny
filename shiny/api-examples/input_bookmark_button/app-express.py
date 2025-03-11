from shiny.express import app_opts, session, ui

app_opts(bookmark_store="url")


ui.markdown(
    "Directions: "
    "\n1. Change the radio button selection below"
    "\n2. Save the bookmark."
    "\n3. Then, refresh your browser page to see the radio button selection has been restored."
)


ui.input_radio_buttons("letter", "Choose a letter", choices=["A", "B", "C"])
ui.input_bookmark_button()


@session.bookmark.on_bookmarked
async def _(url: str):
    await session.bookmark.update_query_string(url)
