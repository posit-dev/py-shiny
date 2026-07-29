from shiny import reactive
from shiny.bookmark import BookmarkState
from shiny.express import app_opts, input, render, session, ui

# Make sure to set the bookmark_store to `"url"` (or `"server"`)
# to store the bookmark information/key in the URL query string.
app_opts(bookmark_store="url")

ui.markdown(
    "Directions: "
    "\n1. Change the radio buttons below"
    "\n2. Refresh your browser."
    "\n3. The radio buttons should be restored to their previous state."
    "\n4. Check the console messages for bookmarking events."
)
ui.hr()
ui.input_radio_buttons(
    "letter",
    "Choose a letter (Store in Bookmark 'input')",
    choices=["A", "B", "C"],
)
ui.input_radio_buttons(
    "letter_values",
    "Choose a letter (Stored in Bookmark 'values' as lowercase)",
    choices=["A", "B", "C"],
)

# Exclude `"letter_values"` from being saved in the bookmark as we'll store it manually for example's sake
# Append or adjust this list as needed.
session.bookmark.exclude.append("letter_values")

lowercase_letter = reactive.value()


@reactive.effect
@reactive.event(input.letter_values)
async def _():
    lowercase_letter.set(input.letter_values().lower())


"Selection:"


@render.code
def letters():
    return str([input.letter(), lowercase_letter()])


# When the user interacts with the input, we will bookmark the state.
@reactive.effect
@reactive.event(input.letter, lowercase_letter, ignore_init=True)
async def _():
    await session.bookmark()


# Before saving state, we can adjust the bookmark state values object
@session.bookmark.on_bookmark
async def _(state: BookmarkState):
    print("Bookmark state:", state.input, state.values, state.dir)
    state.values["lowercase"] = lowercase_letter()


# After saving state, we will update the query string with the bookmark URL.
@session.bookmark.on_bookmarked
async def _(url: str):
    print("Bookmarked url:", url)
    await session.bookmark.update_query_string(url)


@session.bookmark.on_restore
def _(state: BookmarkState):
    print("Restore state:", state.input, state.values, state.dir)

    # Update the radio button selection based on the restored state.
    if "lowercase" in state.values:
        uppercase = state.values["lowercase"].upper()
        # This may produce a small blip in the UI as the original value was restored on the client's HTML request, _then_ a message is received by the client to update the value.
        ui.update_radio_buttons("letter_values", selected=uppercase)


@session.bookmark.on_restored
def _(state: BookmarkState):
    # For rare cases, you can update the UI after the session has been fully restored.
    print("Restored state:", state.input, state.values, state.dir)
