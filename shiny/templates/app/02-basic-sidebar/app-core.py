import seaborn as sns

# Import data from shared.py
from shared import df

from shiny import App, render, ui

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_select(
            "var", "Select variable", choices=["bill_length_mm", "body_mass_g"]
        ),
        ui.input_switch("species", "Group by species", value=True),
        ui.input_switch("show_rug", "Show Rug", value=True),
    ),
    ui.output_plot("hist"),
    title="Hello sidebar!",
)


def server(input, output, session):
    @render.plot
    def hist():
        hue = "species" if input.species() else None
        sns.kdeplot(df, x=input.var(), hue=hue)
        if input.show_rug():
            sns.rugplot(df, x=input.var(), hue=hue, color="black", alpha=0.25)


app = App(app_ui, server)
