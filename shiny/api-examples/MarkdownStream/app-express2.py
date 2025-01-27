import time

import requests

from shiny.express import session, ui


def gen1():
    chunks = ["Hello, World!", "Hello, World!"]
    for chunk in chunks:
        if not session.is_stub_session():
            time.sleep(0.02)
        yield chunk + " "


def gen2():
    chunks = ["Hello, World 2!", "Hello, World 2!"]
    for chunk in chunks:
        if not session.is_stub_session():
            time.sleep(0.02)
        yield chunk + " "


md = ui.MarkdownStream("shiny-readme")
md.ui()
md.stream(gen1())
md.stream(gen2(), clear=False)
