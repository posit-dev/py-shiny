from shiny import ui


def test_panel_main_and_panel_sidebar():
    ps = ui.layout_sidebar(
        ui.panel_sidebar("Sidebar!"),
        ui.panel_main("Main!", TestAttr=True),
    )
    ps_str = str(ps.tagify())
    assert "TestAttr" in ps_str
    assert "Sidebar!" in ps_str
    assert "Main!" in ps_str

    try:
        ui.layout_sidebar(
            None,
            ui.sidebar("Sidebar!"),  # type: ignore
        )
        raise AssertionError("Should have raised TypeError")
    except TypeError as e:
        assert "Please use the `sidebar=` argument" in str(e)

    try:
        ui.layout_sidebar(
            None,  # sidebar
            ui.panel_sidebar("Sidebar!"),
            ui.panel_sidebar("Sidebar!"),
        )
        raise AssertionError("Should have raised TypeError")
    except TypeError as e:
        assert "Only one `sidebar=`" in str(e)

    try:
        ui.layout_sidebar(
            "Sidebar2!",
            ui.panel_sidebar("Sidebar!"),
        )
        raise AssertionError("Should have raised TypeError")
    except TypeError as e:
        assert "Only one `sidebar=`" in str(e)
