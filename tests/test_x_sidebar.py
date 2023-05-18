import shiny.experimental as x


def test_panel_main_and_panel_sidebar():
    ps = x.ui.layout_sidebar(
        x.ui.panel_sidebar("Sidebar!"),
        x.ui.panel_main("Main!", TestAttr=True),
    )
    ps_str = str(ps.tagify())
    assert "TestAttr" in ps_str
    assert "Sidebar!" in ps_str
    assert "Main!" in ps_str
