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

    try:
        x.ui.layout_sidebar(
            None,
            x.ui.sidebar("Sidebar!"),  # type: ignore
        )
        raise AssertionError("Should have raised TypeError")
    except TypeError as e:
        assert "Please use the `sidebar=` argument" in str(e)

    try:
        x.ui.layout_sidebar(
            None,  # sidebar
            x.ui.panel_sidebar("Sidebar!"),
            x.ui.panel_sidebar("Sidebar!"),
        )
        raise AssertionError("Should have raised TypeError")
    except TypeError as e:
        assert "Multiple `panel_sidebar()` calls detected" in str(e)

    try:
        x.ui.layout_sidebar(
            "Sidebar2!",
            x.ui.panel_sidebar("Sidebar!"),
        )
        raise AssertionError("Should have raised TypeError")
    except TypeError as e:
        assert "was supplied along with" in str(e)
