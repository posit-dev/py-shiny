import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from plotnine.data import mtcars

from shiny import App, Inputs, Outputs, Session, reactive, render, ui

nav = ui.navset_pill_list(
    ui.nav_control(ui.p("Choose a package", class_="lead text-center")),
    ui.nav(
        "Plotnine",
        ui.output_plot("plotnine"),
        ui.div(
            {"class": "d-flex justify-content-center", "style": "gap: 5rem"},
            ui.input_select(
                "x", "X variable", choices=list(mtcars.keys()), selected="wt"
            ),
            ui.input_select(
                "y", "Y variable", choices=list(mtcars.keys()), selected="mpg"
            ),
            ui.input_select(
                "color",
                "Color variable",
                choices=list(mtcars.keys()),
                selected="cyl",
            ),
        ),
    ),
    ui.nav(
        "Seaborn",
        ui.output_plot("seaborn"),
        ui.div(
            {"class": "d-flex justify-content-around"},
            ui.input_slider("var", "Variance", min=0.1, max=10, value=2),
            ui.input_slider("cov", "Co-variance", min=0, max=1, value=0.4),
        ),
    ),
    ui.nav("Pandas", ui.output_plot("pandas")),
    ui.nav("Holoviews", ui.output_plot("holoviews", height="600px")),
    ui.nav("xarray", ui.output_plot("xarray")),
    ui.nav("geopandas", ui.output_plot("geopandas")),
    ui.nav("missingno", ui.output_plot("missingno")),
    widths=(2, 10),
    well=False,
)


app_ui = ui.page_fluid(
    ui.panel_title(ui.h2("Py-Shiny static plotting examples", class_="text-center")),
    ui.br(class_="py-3"),
    ui.div(nav, style="max-width: 90%; margin: auto"),
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.Calc
    def fake_data():
        n = 5000
        mean = [0, 0]
        rng = np.random.RandomState(0)
        cov = [(input.var(), input.cov()), (input.cov(), 1 / input.var())]
        return rng.multivariate_normal(mean, cov, n).T

    @output
    @render.plot
    def seaborn():
        x, y = fake_data()
        f, ax = plt.subplots(figsize=(6, 6))
        sns.scatterplot(x=x, y=y, s=5, color=".15")
        sns.histplot(x=x, y=y, bins=50, pthresh=0.1, cmap="mako")
        sns.kdeplot(x=x, y=y, levels=5, color="w", linewidths=1)
        return f

    @output
    @render.plot
    def plotnine():
        from plotnine import (
            aes,
            facet_wrap,
            geom_point,
            ggplot,
            stat_smooth,
            theme,
            theme_bw,
        )

        color_var = input.color()
        if str(mtcars[color_var].dtype) == "int64":
            color_var = f"factor({color_var})"
        return (
            ggplot(mtcars, aes(input.x(), input.y(), color=color_var))
            + geom_point()
            + stat_smooth(method="lm")
            + facet_wrap("~gear")
            + theme_bw(base_size=16)
            + theme(legend_position="top")
        )

    @output
    @render.plot
    def pandas():
        ts = pd.Series(
            np.random.randn(1000), index=pd.date_range("1/1/2000", periods=1000)
        )
        ts = ts.cumsum()
        return ts.plot()

    @output
    @render.plot
    def holoviews():
        import holoviews as hv
        from bokeh.sampledata.les_mis import data as les_mis

        links = pd.DataFrame(les_mis["links"])
        return hv.render(hv.Chord(links), backend="matplotlib")

    @output
    @render.plot
    def xarray():
        import xarray as xr

        airtemps = xr.tutorial.open_dataset("air_temperature")
        air = airtemps.air - 273.15
        air.attrs = airtemps.air.attrs
        air.attrs["units"] = "deg C"
        return air.isel(lon=10, lat=[19, 21, 22]).plot.line(x="time")

    @output
    @render.plot
    def geopandas():
        import geopandas

        nybb_path = geopandas.datasets.get_path("nybb")
        boros = geopandas.read_file(nybb_path)
        boros.set_index("BoroCode", inplace=True)
        boros.sort_index(inplace=True)
        return boros.plot()

    @output
    @render.plot
    def missingno():
        import missingno as msno

        collisions = pd.read_csv(
            "https://raw.githubusercontent.com/ResidentMario/missingno-data/master/nyc_collision_factors.csv"
        )
        return msno.matrix(collisions.sample(250))


app = App(app_ui, server)
