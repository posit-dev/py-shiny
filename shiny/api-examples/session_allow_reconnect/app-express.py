from shiny.express import input, render, session, ui

ui.markdown("""
    This app lets the browser reconnect after its connection to the server
    drops. Use the button below to close the connection: instead of the usual
    "Disconnected from server" overlay, you should see a countdown dialog while
    the client reconnects, and the counter below should keep working once it
    does.

    `"force"` is used here so the reconnect is attempted even when the hosting
    environment does not support resuming sessions. Use `True` in production so
    the client only reconnects where the session is actually kept alive.
    """)

ui.input_action_button(
    "close", "Close the connection", onclick="Shiny.shinyapp.$socket.close()"
)
ui.input_action_button("count", "Count")

session.allow_reconnect("force")


@render.text
def counter():
    return f"Clicked {input.count()} times."
