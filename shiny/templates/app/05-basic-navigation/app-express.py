import seaborn as sns

# Import data from shared.py
from shared import df

from shiny.express import input, render, ui

ui.page_opts(title="Shiny navigation components")

ui.nav_spacer()  # Push the navbar items to the right

footer = ui.input_select(
    "var", "Select variable", choices=["bill_length_mm", "body_mass_g"]
)

with ui.nav_panel("Page 1"):
    with ui.navset_card_underline(title="Penguins data", footer=footer):
        with ui.nav_panel("Plot"):

            @render.plot
            def hist():
                p = sns.histplot(
                    df, x=input.var(), facecolor="#007bc2", edgecolor="white"
                )
                return p.set(xlabel=None)

        with ui.nav_panel("Table"):

            @render.data_frame
            def data():
                return df[["species", "island", input.var()]]


with ui.nav_panel("Page 2"):
    "This is the second 'page'."
