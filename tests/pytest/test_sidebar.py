import pytest

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


@pytest.mark.parametrize(
    "open_value, expected",
    [
        ("closed", {"desktop": "closed", "mobile": "closed"}),
        ("open", {"desktop": "open", "mobile": "open"}),
        ("always", {"desktop": "always", "mobile": "always"}),
        ("desktop", {"desktop": "open", "mobile": "closed"}),
    ],
)
def test_sidebar_open_string_values(open_value, expected):
    assert ui.sidebar(open=open_value).open() == ui.sidebar(open=expected).open()


def test_sidebar_assigns_input_binding_class_if_id_provided():
    s = ui.sidebar(id="my_sidebar")

    assert s.tagify()[0].has_class("bslib-sidebar-input")
    assert s.tagify()[0].attrs["id"] == "my_sidebar"


def test_sidebar_assigns_random_id_if_collapsible_and_id_not_provided():
    s_open = ui.sidebar(open="open").tagify()
    assert s_open[0].attrs["id"].startswith("bslib_sidebar_")
    assert s_open[0].attrs["id"] == s_open[1].attrs["aria-controls"]

    s_closed = ui.sidebar(open="closed").tagify()
    assert s_closed[0].attrs["id"].startswith("bslib_sidebar_")
    assert s_closed[0].attrs["id"] == s_closed[1].attrs["aria-controls"]

    s_always = ui.sidebar(open="always").tagify()
    assert "id" not in s_always[0].attrs
    assert "aria-controls" not in s_always[1].attrs


def test_sidebar_sets_aria_expanded_on_collapse_toggle():
    def get_sidebar_collapse_aria_expanded(open: str) -> str:
        return ui.sidebar(open=open).tagify()[1].attrs["aria-expanded"]

    assert get_sidebar_collapse_aria_expanded("open") == "true"
    assert get_sidebar_collapse_aria_expanded("closed") == "false"
    assert get_sidebar_collapse_aria_expanded("desktop") == "true"
    assert "aria-expanded" not in ui.sidebar(open="always").tagify()[1].attrs


def test_sidebar_throws_for_invalid_open():
    try:
        ui.sidebar(open="bad")
        raise AssertionError("Should have raised ValueError")
    except ValueError as e:
        assert "`open` must be a non-empty string" in str(e)

    try:
        ui.sidebar(open=("closed", "open"))
        raise AssertionError("Should have raised ValueError")
    except ValueError as e:
        assert "`open` must be one of" in str(e)

    try:
        ui.sidebar(open={"desktop": "bad"})
        raise AssertionError("Should have raised ValueError")
    except ValueError as e:
        assert "`desktop` must be one of" in str(e)

    try:
        ui.sidebar(open={"widescreen": "open"})
        raise AssertionError("Should have raised TypeError")
    except TypeError as e:
        assert "widescreen" in str(e)


def test_sidebar_updates_default_without_modifying_original():
    s1 = ui.sidebar()
    s2 = s1._set_default_open("closed")

    assert s1.open() == ui.sidebar().open()
    assert s2.open() == ui.sidebar(open="closed").open()

    # Insert user preference in front of default
    s1.open({"desktop": "always"})
    assert s1.open().desktop == "always"

    # Remove user preference, should revert to default
    s1.open(None)
    assert s1.open() == ui.sidebar().open()
