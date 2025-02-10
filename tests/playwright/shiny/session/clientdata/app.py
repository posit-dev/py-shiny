# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false
import matplotlib.pyplot as plt
import numpy as np

from shiny.express import input, render, session, ui

with ui.sidebar(open="closed"):
    ui.input_slider("obs", "Number of observations:", min=0, max=1000, value=500)


@render.code
def clientdatatext():
    client_data = session.clientdata
    return "\n".join(
        [f"{name} = {client_data[name]()}" for name in reversed(dir(client_data))]
    )


@render.plot
def myplot():
    plt.figure()
    plt.hist(np.random.normal(size=input.obs()))  # type: ignore
    plt.title("This is myplot")
