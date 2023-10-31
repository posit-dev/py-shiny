from __future__ import annotations

from shiny import reactive, session

print("Loading shared!")

x = 123

with session.session_context(None):
    rv = reactive.Value(-1)
