import textwrap

from starlette.requests import Request

from shiny import App, Inputs, Outputs, Session, reactive, render, ui
from shiny.bookmark import BookmarkState


# App UI **must** be a function to ensure that each user restores their own UI values.
def app_ui(request: Request):
    return ui.page_fluid(
        ui.markdown(
            "Directions: "
            "\n1. Change the radio buttons below"
            "\n2. Refresh your browser."
            "\n3. The radio buttons should be restored to their previous state."
            "\n4. Check the console messages for bookmarking events."
        ),
        ui.hr(),
        ui.input_radio_buttons(
            "letter",
            "Choose a letter (Store in Bookmark 'input')",
            choices=["A", "B", "C"],
        ),
        "Selection:",
        ui.output_code("letter_out"),
        ui.input_action_button("stop_session", "Stop session"),
        ui.tags.script(
            textwrap.dedent(
                """
                {
                    console.log("adding shiny:connected and shiny:disconnected event listeners");
                    let latest_url = null;
                    // window.document.onshiny:disconnected
                    $(document).on("shiny:connected", function(event) {
                        // The session has ended, so we can update the URL with the bookmark URL
                        console.log("Session connected, setting latest_url to:", event);
                    });
                    $(document).on("shiny:disconnected", function(event) {
                        // The session has ended, so we can update the URL with the bookmark URL
                        console.log("Session disconnected, setting latest_url to:", latest_url);
                        // window.location = latest_url;
                        window.history.replaceState(null, null, latest_url);

                    });

                    Shiny.addCustomMessageHandler("updateUrlOnSessionDisconnect", function(message) {
                        // Update the URL with the bookmark URL
                        console.log("Received latest bookmark URL:", message.url);
                        latest_url = message.url;
                    })
                }
                """
            )
        ),
    )


def server(input: Inputs, output: Outputs, session: Session):

    @reactive.effect
    @reactive.event(input.stop_session)
    async def _():
        print("Stopping session...")
        await session.stop()

    @render.code
    def letter_out():
        return str(input.letter())

    # When the user interacts with the input, we will bookmark the state.
    @reactive.effect
    @reactive.event(input.letter, ignore_init=True)
    async def _():
        await session.bookmark()

    # After saving state, we will update the query string with the bookmark URL.
    @session.bookmark.on_bookmarked
    async def _(url: str):
        print("Session end url:", url)
        await session.bookmark.update_on_session_disconnect(url)


# Make sure to set the bookmark_store to `"url"` (or `"server"`)
# to store the bookmark information/key in the URL query string.
app = App(app_ui, server, bookmark_store="url")
