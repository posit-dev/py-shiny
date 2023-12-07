from faicons import icon_svg

from shiny import *
from shiny.types import ImgData
from shiny.ui import HTML, Tag, tags

app_ui = ui.page_fluid(
    ui.panel_title("Hello Shiny UI"),
    ui.layout_sidebar(
        ui.panel_sidebar(
            ui.input_slider(
                "n", "input_slider()", min=10, max=100, value=50, step=5, animate=True
            ),
            ui.input_date("date", "input_date()"),
            ui.input_date_range("date_rng", "input_date_range()"),
            ui.input_text("txt", "input_text()", placeholder="Input some text"),
            ui.input_text_area(
                "txt_area", "input_text_area()", placeholder="Input some text"
            ),
            ui.input_numeric("num", "input_numeric()", 20),
            ui.input_password("password", "input_password()"),
            ui.input_checkbox("checkbox", "input_checkbox()"),
            ui.input_checkbox_group(
                "checkbox_group",
                "input_checkbox_group()",
                {"a": "Choice 1", "b": "Choice 2"},
                selected=["a", "b"],
                inline=True,
            ),
            ui.input_radio_buttons(
                "radio", "input_radio()", {"a": "Choice 1", "b": "Choice 2"}
            ),
            ui.input_select(
                "select",
                "input_select()",
                {
                    "a": "Choice A",
                    "Group B": {"b1": "Choice B1", "b2": "Choice B2"},
                    "Group C": {"c1": "c1", "c2": "c2"},
                },
            ),
            ui.input_action_button(
                "button",
                "input_action_button()",
                icon=icon_svg("check"),
                class_="btn-primary",
            ),
            ui.input_file("file", "File upload"),
        ),
        ui.panel_main(
            # ui.output_plot("plot"),
            ui.navset_tab_card(
                # TODO: output_plot() within a tab not working?
                ui.nav_panel("Inputs", ui.output_ui("inputs"), icon=icon_svg("code")),
                ui.nav_panel(
                    "Image",
                    ui.output_plot("plot"),
                    icon=icon_svg("image"),
                ),
                ui.nav_panel(
                    "Misc",
                    ui.input_action_link(
                        "link", "Show notification/progress", icon=icon_svg("info")
                    ),
                    tags.br(),
                    ui.input_action_button(
                        "btn",
                        "Show modal",
                        icon=icon_svg("info"),
                        class_="btn-primary",
                    ),
                    ui.panel_fixed(
                        ui.panel_well(
                            "A fixed, draggable, panel",
                            ui.input_checkbox("checkbox2", "Check me!"),
                            ui.panel_conditional(
                                "input.checkbox2 == true", "Thanks for checking!"
                            ),
                        ),
                        draggable=True,
                        width="fit-content",
                        height="50px",
                        top="50px",
                        right="50px",
                    ),
                    # icon=icon_svg("code"),
                ),
            ),
        ),
    ),
)


import matplotlib.pyplot as plt
import numpy as np


def server(input: Inputs, output: Outputs, session: Session):
    @output()
    @render.ui()
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
    @render.plot(alt="A histogram")
    def plot():
        fig, ax = plt.subplots()
        ax.hist(x_rand, int(input.n()), density=True)
        return fig

    @output()
    @render.image()
    def image():
        from pathlib import Path

        dir = Path(__file__).resolve().parent
        img: ImgData = {"src": str(dir / "rstudio-logo.png"), "width": "150px"}
        return img

    @reactive.Effect()
    def _():
        btn = input.btn()
        if btn and btn > 0:
            ui.modal_show(
                ui.modal(
                    "Hello there!",
                    easy_close=True,
                    footer=ui.modal_button("Dismiss", class_="btn-primary"),
                )
            )

    @reactive.Effect()
    def _():
        link = input.link()
        if link and link > 0:
            ui.notification_show("A notification!")
            p = ui.Progress()
            import time

            for i in range(30):
                p.set(i / 30, message="Computing")
                time.sleep(0.1)
            p.close()


app = App(app_ui, server)
