from shiny import ui

_s = ui.sidebar("Sidebar!")
_m = "Body"
_ps = ui.panel_sidebar("Panel Sidebar!")
_pm = ui.panel_main("Panel Main!", TestAttr=True)


def test_panel_main_and_panel_sidebar():
    ps = ui.layout_sidebar(_ps, _pm)
    ps_str = str(ps.tagify())
    assert "TestAttr" in ps_str
    assert "Panel Sidebar!" in ps_str
    assert "Panel Main!" in ps_str

    # OK
    ui.layout_sidebar(_s)
    ui.layout_sidebar(_s, None)

    try:
        ui.layout_sidebar(_s, _s)
        raise AssertionError("Should have raised ValueError")
    except ValueError as e:
        assert "multiple `sidebar()` objects" in str(e)

    try:
        ui.layout_sidebar(None, _ps)  # pyright: ignore[reportArgumentType]
        raise AssertionError("Should have raised ValueError")
    except ValueError as e:
        assert "not being supplied with a `sidebar()` object." in str(e)

    try:
        ui.layout_sidebar(_s, _pm)
        raise AssertionError("Should have raised ValueError")
    except ValueError as e:
        assert "is not being used with `panel_sidebar()`" in str(e)

    try:
        ui.layout_sidebar(_ps, None, _pm)
        raise AssertionError("Should have raised ValueError")
    except ValueError as e:
        assert "not being supplied as the second argument" in str(e)
    try:
        ui.layout_sidebar(_ps, _pm, None, "42")
        raise AssertionError("Should have raised ValueError")
    except ValueError as e:
        assert "Unexpected extra legacy `*args`" in str(e)
