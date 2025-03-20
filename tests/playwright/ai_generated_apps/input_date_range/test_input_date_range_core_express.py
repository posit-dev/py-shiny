from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.pytest import create_app_fixture
from shiny.run import ShinyAppProc

app = create_app_fixture(["app-core.py", "app-express.py"])


def test_date_range_input(page: Page, app: ShinyAppProc) -> None:
    page.goto(app.url)

    # Initialize the date range input controller
    date_range = controller.InputDateRange(page, "date_range")

    # Test selected_range output
    selected_range = controller.OutputText(page, "selected_range")
    selected_range.expect_value("Start date: 2023-01-01\nEnd date: 2023-12-31")

    # Test initial properties
    date_range.expect_label("Select Date Range")
    date_range.expect_value(("01/01/2023", "12/31/2023"))  # Test initial values
    date_range.expect_min_date("2020-01-01")  # Test minimum date
    date_range.expect_max_date("2025-12-31")  # Test maximum date
    date_range.expect_format("mm/dd/yyyy")  # Test date format
    date_range.expect_startview("decade")  # Test start view
    date_range.expect_weekstart("1")  # Test week start (Monday)
    date_range.expect_language("en")  # Test language setting
    date_range.expect_separator(" → ")  # Test separator
    date_range.expect_width("100%")  # Test width
    date_range.expect_autoclose("true")  # Test autoclose

    # Test setting new values
    date_range.set(("06/01/2023", "06/30/2023"))
    date_range.expect_value(("06/01/2023", "06/30/2023"))

    # Test setting only start date
    date_range.set(("07/01/2023", None))
    date_range.expect_value(("07/01/2023", "06/30/2023"))

    # Test setting only end date
    date_range.set((None, "07/31/2023"))
    date_range.expect_value(("07/01/2023", "07/31/2023"))

    # Test setting dates at the boundaries
    date_range.set(("01/01/2020", "12/31/2025"))  # Min and max dates
    date_range.expect_value(("01/01/2020", "12/31/2025"))
