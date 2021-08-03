# To run this app:
#   python3 app.py

# Connect from another terminal:
#   nc localhost 8888
# Then send JSON messages, e.g.:
#   {"n":1}
#   {"n":4}

from reactives import Reactive, ReactiveValues
from shinyapp import ShinyApp
from shinysession import Outputs
from ui import *

ui = page.fluid(   
    output.text("txt"),
    input.slider("n", "Choose n", 0, 100, 50),
    title = "Prism demo"
)

print(ui)


def server(input: ReactiveValues, output: Outputs):
    print("Running user server function")

    @Reactive
    def r():
        print("Executing reactive r()")
        return input["n"] * 2

    @output.set("txt")
    def _():
        print("Executing output txt")
        return f"r() is {r()}"

    @output.set("txt2")
    def _():
        print("Executing output txt2")
        return f"r() is {r()}"


app = ShinyApp(ui, server)

app.run()
