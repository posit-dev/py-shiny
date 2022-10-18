from conftest import ShinyAppProc, create_example_fixture
from playwright.sync_api import Page, expect

app = create_example_fixture("static_plots")


def test_static_plots(page: Page, app: ShinyAppProc):
    page.goto(app.url)

    # Click on each plot library type from the navset_pill card menu on the left
    # and parallely verify plot is rendered

      # Two steps to check plot is shown
      #1. checking the plot has correct output classes
      #2. Take a screenshot and compare?
          #a. https://github.com/kumaraditya303/pytest-playwright-snapshot
          #b. https://github.com/symon-storozhenko/pytest-playwright-visual
      #3. If not screenshot, check base64 image code?

    #TODO: Navigation - Nav-pill-list. Add a Class and use in the test

    # PLOTNINE
    page.locator(".nav.nav-pills .nav-item a[data-value='Plotnine']")
    plot1 = page.locator("#plotnine")
    # Adding this step to make sure plot loads and visible
    plot1.hover()
    expect(plot1).to_have_class("shiny-image-output shiny-plot-output shiny-bound-output")

    # SEABORN
    page.locator(".nav.nav-pills .nav-item a[data-value='Seaborn']").click()
    plot2 = page.locator("#seaborn")
    plot2.hover()
    expect(plot2).to_have_class("shiny-image-output shiny-plot-output shiny-bound-output")

    # PANDAS
    page.locator(".nav.nav-pills .nav-item a[data-value='Pandas']").click()
    plot3 = page.locator("#pandas")
    plot3.hover()
    expect(plot3).to_have_class("shiny-image-output shiny-plot-output shiny-bound-output")

    # HOLOVIEWS
    page.locator(".nav.nav-pills .nav-item a[data-value='Holoviews']").click()
    plot4 = page.locator("#holoviews")
    plot4.hover()
    expect(plot4).to_have_class("shiny-image-output shiny-plot-output shiny-bound-output")

    # XARRAY
    page.locator(".nav.nav-pills .nav-item a[data-value='xarray']").click()
    plot5 = page.locator("#xarray")
    plot5.hover()
    expect(plot5).to_have_class("shiny-image-output shiny-plot-output shiny-bound-output")

    # GEOPANDAS
    page.locator(".nav.nav-pills .nav-item a[data-value='geopandas']").click()
    plot6 = page.locator("#geopandas")
    plot6.hover()
    expect(plot6).to_have_class("shiny-image-output shiny-plot-output shiny-bound-output")

    # Missingno
    page.locator(".nav.nav-pills .nav-item a[data-value='missingno']").click()
    plot7 = page.locator("#missingno")
    plot7.hover()
    expect(plot7).to_have_class("shiny-image-output shiny-plot-output shiny-bound-output")








