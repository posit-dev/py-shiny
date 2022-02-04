# This will load the shiny module dynamically, without having to install it.
# This makes the debug/run cycle quicker.
import os
import sys

shiny_module_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, shiny_module_dir)


import shiny.ui_toolkit as st
from shiny import *
from htmltools import tags, HTML, Tag
from fontawesome import icon_svg

ui = st.page_fluid(
    st.panel_title("Hello prism ui"),
    st.layout_sidebar(
        st.panel_sidebar(
            st.input_slider(
                "n", "input_slider()", min=10, max=100, value=50, step=5, animate=True
            ),
            st.input_date("date", "input_date()"),
            st.input_date_range("date_rng", "input_date_range()"),
            st.input_text("txt", "input_text()", placeholder="Input some text"),
            st.input_text_area(
                "txt_area", "input_text_area()", placeholder="Input some text"
            ),
            st.input_numeric("num", "input_numeric()", 20),
            st.input_password("password", "input_password()"),
            st.input_checkbox("checkbox", "input_checkbox()"),
            st.input_checkbox_group(
                "checkbox_group",
                "input_checkbox_group()",
                {"a": "Choice 1", "b": "Choice 2"},
                selected=["a", "b"],
                inline=True,
            ),
            st.input_radio_buttons(
                "radio", "input_radio()", {"a": "Choice 1", "b": "Choice 2"}
            ),
            st.input_select(
                "select",
                "input_select()",
                {
                    "a": "Choice A",
                    "Group B": {"b1": "Choice B1", "b2": "Choice B2"},
                    "Group C": {"c1": "c1", "c2": "c2"},
                },
            ),
            st.input_action_button(
                "button", "input_action_button()", icon=icon_svg("check")
            ),
            st.input_file("file", "File upload"),
        ),
        st.panel_main(
            st.output_plot("plot"),
            st.navs_tab_card(
                # TODO: output_plot() within a tab not working?
                st.nav("Inputs", st.output_ui("inputs"), icon=icon_svg("code")),
                st.nav(
                    "Image",
                    st.output_image("image", inline=True),
                    icon=icon_svg("image"),
                ),
                st.nav(
                    "Misc",
                    st.input_action_link(
                        "link", "Show notification/progress", icon=icon_svg("info")
                    ),
                    tags.br(),
                    st.input_action_button(
                        "btn", "Show modal", icon=icon_svg("info-circle")
                    ),
                    st.panel_fixed(
                        st.panel_well(
                            "A fixed, draggable, panel",
                            st.input_checkbox("checkbox2", "Check me!"),
                            st.panel_conditional(
                                "input.checkbox2 == true", "Thanks for checking!"
                            ),
                        ),
                        draggable=True,
                        width="fit-content",
                        height="50px",
                        top="50px",
                        right="50px",
                    ),
                    icon=icon_svg("code"),
                ),
            ),
        ),
    ),
)


import numpy as np
import matplotlib.pyplot as plt


def server(input: Inputs, output: Outputs, session: Session):
    @output()
    @render_ui()
    def inputs() -> Tag:
        vals = [
            f"<code>input_date()</code> {input.date()}",
            f"<code>input_date_range()</code>: {input.date_rng()}",
            f"<code>input_text()</code>: {input.txt()}",
            f"<code>input_text_area()</code>: {input.txt_area()}",
            f"<code>input_numeric()</code>: {input.num()}",
            f"<code>input_password()</code>: {input.password()}",
            f"<code>input_checkbox()</code>: {input.checkbox()}",
            f"<code>input_checkbox_group()</code>: {input.checkbox_group()}",
            f"<code>input_radio()</code>: {input.radio()}",
            f"<code>input_select()</code>: {input.select()}",
            f"<code>input_action_button()</code>: {input.button()}",
        ]
        return tags.pre(HTML("\n".join(vals)))

    np.random.seed(19680801)
    x_rand = 100 + 15 * np.random.randn(437)

    @output()
    @render_plot(alt="A histogram")
    def plot():
        fig, ax = plt.subplots()
        ax.hist(x_rand, int(input.n()), density=True)
        return fig

    @output()
    @render_image()
    def image():
        from pathlib import Path

        dir = Path(__file__).resolve().parent
        return {"src": dir / "rstudio-logo.png", "width": "150px"}

    @reactive.effect()
    def _():
        btn = input.btn()
        if btn and btn > 0:
            st.modal_show(st.modal("Hello there!", easy_close=True))

    @reactive.effect()
    def _():
        link = input.link()
        if link and link > 0:
            notification_show("A notification!")
            p = Progress()
            import time

            for i in range(30):
                p.set(i / 30, message="Computing")
                time.sleep(0.1)
            p.close()


app = App(ui, server)
