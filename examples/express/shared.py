# This is not a Shiny application; it is meant to be imported by shared_app.py.

from shiny import reactive, session

# Print this at the console to make it clear that shared.py is loaded just once per run
# of the app; each additional session does not result in this file loading again.
print("Loading shared.py!")

# This is a variable that can be used and shared across multiple sessions. This can be
# useful for large data, or values that are expensive to compute. It can also be useful
# for mutable objects that you want to share across sessions.
data = ["This", "is", "a", "list", "of", "words"]

# Any reactive objects should be created without a session context.
with session.session_context(None):
    # This reactive value can be used by multiple sessions; if it is invalidated (in
    # other words, if the value is changed), it will trigger invalidations in all of
    # those sessions.
    rv = reactive.value(50)
