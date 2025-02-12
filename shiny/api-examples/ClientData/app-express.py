# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false
import matplotlib.pyplot as plt
import numpy as np

from shiny.express import input, render, session, ui

with ui.sidebar(open="closed"):
    ui.input_slider("obs", "Number of observations:", min=0, max=1000, value=500)

ui.markdown(
    """
#### `session.clientdata` values

The following methods are available from the `session.clientdata` object and allow you
to reactively read the client data values from the browser.
"""
)


@render.code
def clientdatatext():
    return f"""
    .url_hash()         -> {session.clientdata.url_hash()}
    .url_hash_initial() -> {session.clientdata.url_hash_initial()}
    .url_hostname()     -> {session.clientdata.url_hostname()}
    .url_pathname()     -> {session.clientdata.url_pathname()}
    .url_port()         -> {session.clientdata.url_port()}
    .url_protocol()     -> {session.clientdata.url_protocol()}
    .url_search()       -> {session.clientdata.url_search()}
    .pixelratio()       -> {session.clientdata.pixelratio()}

    .output_height("myplot")       -> {session.clientdata.output_height("myplot")}
    .output_width("myplot")        -> {session.clientdata.output_width("myplot")}
    .output_hidden("myplot")       -> {session.clientdata.output_hidden("myplot")}
    .output_bg_color("myplot")     -> {session.clientdata.output_bg_color("myplot")}
    .output_fg_color("myplot")     -> {session.clientdata.output_fg_color("myplot")}
    .output_accent_color("myplot") -> {session.clientdata.output_accent_color("myplot")}
    .output_font("myplot")         -> {session.clientdata.output_font("myplot")}
    """


@render.plot
def myplot():
    plt.figure()
    plt.hist(np.random.normal(size=input.obs()))  # type: ignore
    plt.title("This is myplot")
