# This will load the shiny module dynamically, without having to install it.
# This makes the debug/run cycle quicker.
import os
import sys
shiny_module_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, shiny_module_dir)

from htmltools import *
from shiny import *
import numpy as np
import matplotlib.pyplot as plt

ui = page_fluid(
    panel_title("Hello prism ui"),
    layout_sidebar(
        panel_sidebar(
            input_file("file", "File upload"),
            input_slider("n", "input_slider()", 0, 100, 50),
            input_date("date", "input_date()"),
            input_date_range("date_rng", "input_date_range()"),
            input_text("txt", "input_text()", placeholder="Input some text"),
            input_text_area("txt_area", "input_text_area()", placeholder="Input some text"),
            input_button("btn", "input_button()"),
            input_link("link", "input_link()"),
            input_checkbox("checkbox", "input_checkbox()"),
            input_checkbox_group(
                "checkbox_group", "input_checkbox_group()",
                {"Choice 1": "a", "Choice 2": "b"},
                selected="b", inline=True
            ),
            input_radio_buttons("radio", "input_radio()", {"Choice 1": "a", "Choice 2": "b"})
            #input_select("select", "input_select()", "Select me"),
         ),
         panel_main(
             output_image("image", inline = True),
             output_plot("plot"),
             panel_fixed(
                 panel_well(
                    "A fixed, draggable, panel",
                     input_checkbox("checkbox2", "Check me!"),
                     panel_conditional("input.checkbox2 == true", "Thanks for checking!")
                  ),
                  draggable=True,
                  width="fit-content",
                  height="50px",
                  top = "50px",
                  right = "50px"
             ),
             output_text("date_val"),
             output_text("date_rng_val")
         )
    )
)

def server(s: ShinySession):
  @s.output("date_val")
  def _() -> str:
      return f"The date is {s.input['date']}"

  @s.output("date_rng_val")
  def _() -> str:
      return f"The date range is {s.input['date_rng']}"

  @s.output("plot")
  @render.plot(alt="A histogram")
  def _():
      np.random.seed(19680801)
      x = 100 + 15 * np.random.randn(437)
      fig, ax = plt.subplots()
      ax.hist(x, s.input["n"], density=True)
      return fig

  @s.output("image")
  @render.image()
  def _():
    from pathlib import Path
    dir = Path(__file__).resolve().parent
    return {"src": dir / "rstudio-logo.png", "width": "150px"}


app = ShinyApp(ui, server)
if __name__ == "__main__":
  app.run()
