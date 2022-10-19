from conftest import ShinyAppProc, create_example_fixture
from playwright.sync_api import Page, expect
import re

from controls import NavControls


app = create_example_fixture("static_plots")


def test_static_plots(page: Page, app: ShinyAppProc):
    page.goto(app.url)

    plot1 = page.locator("#plotnine")
    image1 = plot1.locator("img")
    expect(image1).to_have_attribute("src", re.compile(r"^data:image/png;base64,iVBOR"))
    expect(plot1).to_have_class("shiny-image-output shiny-plot-output shiny-bound-output")

    nav_seaborn = NavControls(page, "nav-pills", "Seaborn")
    nav_seaborn.loc.click()
    plot2 = page.locator("#seaborn")
    image2 = plot2.locator("img")
    expect(image2).to_have_attribute("src", re.compile(r"^data:image/png;base64,iVBOR"))
    expect(plot2).to_have_class("shiny-image-output shiny-plot-output shiny-bound-output")

    nav_pandas = NavControls(page, "nav-pills", "Pandas")
    nav_pandas.loc.click()
    plot3 = page.locator("#pandas")
    image3 = plot3.locator("img")
    expect(image3).to_have_attribute("src", re.compile(r"^data:image/png;base64,iVBOR"))
    expect(plot3).to_have_class("shiny-image-output shiny-plot-output shiny-bound-output")

    nav_holoviews = NavControls(page, "nav-pills", "Holoviews")
    nav_holoviews.loc.click()
    plot4 = page.locator("#holoviews")
    image4 = plot4.locator("img")
    expect(image4).to_have_attribute("src", re.compile(r"^data:image/png;base64,iVBOR"))
    expect(plot4).to_have_class("shiny-image-output shiny-plot-output shiny-bound-output")

    nav_xarray = NavControls(page, "nav-pills", "xarray")
    nav_xarray.loc.click()
    plot5 = page.locator("#xarray")
    image5 = plot5.locator("img")
    expect(image5).to_have_attribute("src", re.compile(r"^data:image/png;base64,iVBOR"))
    expect(plot5).to_have_class("shiny-image-output shiny-plot-output shiny-bound-output")

    nav_geopandas = NavControls(page, "nav-pills", "geopandas")
    nav_geopandas.loc.click()
    plot6 = page.locator("#geopandas")
    image6 = plot6.locator("img")
    expect(image6).to_have_attribute("src", re.compile(r"^data:image/png;base64,iVBOR"))
    expect(plot6).to_have_class("shiny-image-output shiny-plot-output shiny-bound-output")

    nav_missingno = NavControls(page, "nav-pills", "missingno")
    nav_missingno.loc.click()
    plot7 = page.locator("#missingno")
    image7 = plot7.locator("img")
    expect(image7).to_have_attribute("src", re.compile(r"^data:image/png;base64,iVBOR"))
    expect(plot7).to_have_class("shiny-image-output shiny-plot-output shiny-bound-output")








