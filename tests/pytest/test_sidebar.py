from __future__ import annotations

from typing import Literal

import pytest
from htmltools import Tag, TagAttrValue

from shiny import ui
from shiny.ui._sidebar import SidebarOpenSpec, SidebarOpenValue

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
def test_sidebar_open_string_values(
    open_value: SidebarOpenValue, expected: SidebarOpenSpec
):
    assert ui.sidebar(open=open_value).open() == ui.sidebar(open=expected).open()


def get_sidebar_tags(sb: ui.Sidebar) -> tuple[Tag, Tag]:
    sidebar, collapse = sb.tagify()
    assert isinstance(sidebar, Tag)
    assert isinstance(collapse, Tag)
    return sidebar, collapse


def test_sidebar_assigns_input_binding_class_if_id_provided():
    sidebar_tag, _ = get_sidebar_tags(ui.sidebar(id="my_sidebar"))

    assert sidebar_tag.has_class("bslib-sidebar-input")
    assert sidebar_tag.attrs["id"] == "my_sidebar"


def test_sidebar_assigns_random_id_if_collapsible_and_id_not_provided():
    s_open_sb, s_open_collapse = get_sidebar_tags(ui.sidebar(open="open"))

    assert s_open_sb.attrs["id"].startswith("bslib_sidebar_")
    assert s_open_sb.attrs["id"] == s_open_collapse.attrs["aria-controls"]

    s_closed_sb, s_closed_collapse = get_sidebar_tags(ui.sidebar(open="closed"))
    assert s_closed_sb.attrs["id"].startswith("bslib_sidebar_")
    assert s_closed_sb.attrs["id"] == s_closed_collapse.attrs["aria-controls"]

    s_always_sb, s_always_collapse = get_sidebar_tags(ui.sidebar(open="always"))
    assert "id" not in s_always_sb.attrs
    assert "aria-controls" not in s_always_collapse.attrs


def test_sidebar_sets_aria_expanded_on_collapse_toggle():
    def get_sidebar_collapse_aria_expanded(
        open: SidebarOpenValue | Literal["desktop"],
    ) -> TagAttrValue:
        _, collapse_tag = get_sidebar_tags(ui.sidebar(open=open))
        return collapse_tag.attrs["aria-expanded"]

    assert get_sidebar_collapse_aria_expanded("open") == "true"
    assert get_sidebar_collapse_aria_expanded("closed") == "false"
    assert get_sidebar_collapse_aria_expanded("desktop") == "true"

    _, collapse_always = get_sidebar_tags(ui.sidebar(open="always"))
    assert "aria-expanded" not in collapse_always.attrs


def test_sidebar_throws_for_invalid_open():
    with pytest.raises(ValueError, match="`open` must be a non-empty string"):
        ui.sidebar(open="bad")  # pyright: ignore[reportArgumentType]

    with pytest.raises(ValueError, match="`open` must be one of"):
        ui.sidebar(open=("closed", "open"))  # pyright: ignore[reportArgumentType]

    with pytest.raises(ValueError, match="`desktop` must be one of"):
        ui.sidebar(open={"desktop": "bad"})  # pyright: ignore[reportArgumentType]

    with pytest.raises(TypeError, match="widescreen"):
        ui.sidebar(open={"widescreen": "open"})  # pyright: ignore[reportArgumentType]
