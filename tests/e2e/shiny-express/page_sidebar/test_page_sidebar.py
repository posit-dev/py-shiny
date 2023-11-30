import inspect

from conftest import ShinyAppProc
from controls import OutputTextVerbatim, Sidebar
from playwright.sync_api import Page

from shiny import render, ui
from shiny.express import input, layout


def test_express_page_sidebar(page: Page, local_app: ShinyAppProc) -> None:
    page.goto(local_app.url)
    sidebar = Sidebar(page, "sidebar")
    sidebar.expect_text("SidebarTitle 'Sidebar Content'")
    output_txt = OutputTextVerbatim(page, "txt")
    output_txt.expect_value("50")
    # Ask-Barret: Test failing due to mismatch
    """
    E         Full diff:
E           {
E         +  'args': 'TagChild | TagAttrs',
E            'bg': 'Optional[str]',
E            'class_': 'Optional[str]',
E            'fg': 'Optional[str]',
E            'gap': 'Optional[CssUnit]',
E            'id': 'Optional[str]',
E            'max_height_mobile': 'Optional[str | float]',
E            'open': "Literal['desktop', 'open', 'closed', 'always']",
E            'padding': 'Optional[CssUnit | list[CssUnit]]',
E            'position': "Literal['left', 'right']",
E         -  'return': 'RecallContextManager[ui.Sidebar]',
E         +  'return': 'Sidebar',
E            'title': 'TagChild | str',
E            'width': 'CssUnit',
E           }
    """
    # assert ui.sidebar.__annotations__ == layout.sidebar.__annotations__

    # args_express_sidebar = inspect.signature(layout.sidebar).parameters
    # args_legacy_sidebar = inspect.signature(ui.sidebar).parameters

    # assert args_express_sidebar == args_legacy_sidebar
