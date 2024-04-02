from shiny.express import render
from shiny.types import SafeException


@render.ui
def safe():
    # This error _won't_ be sanitized when deployed
    raise SafeException("This is a safe exception")


@render.ui
def unsafe():
    # This error _will_ be sanitized when deployed
    raise Exception("This is an unsafe exception")
