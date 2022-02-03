# To run this app:
#   python3 app.py

# Then point web browser to:
#   http://localhost:8000/

import shiny.ui_toolkit as st
from shiny import *

ui = st.page_fluid(
    st.input_slider("n", "N", 0, 100, 20),
    st.output_text_verbatim("txt", placeholder=True),
)

# A reactive.Value which is exists outside of the session.
shared_val = reactive.Value(None)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.calc()
    def r():
        if input.n() is None:
            return
        return input.n() * 2

    @output()
    @render_text()
    async def txt():
        val = r()
        return f"n*2 is {val}, session id is {session.id}"


app = App(ui, server)
