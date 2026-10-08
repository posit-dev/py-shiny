from __future__ import annotations

import re
from typing import Literal

import pytest
from htmltools import HTML, TagAttrValue, TagifiedTag, TagifiedTagList, TagList

from shiny import ui
from shiny.ui._sidebar import SidebarOpenSpec, SidebarOpenValue, SidebarRole


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


def get_sidebar_tags(sb: ui.Sidebar) -> tuple[TagifiedTag, TagifiedTag]:
    # Sidebar.tagify() returns a TagifiedTagList of two TagifiedTags.
    tagified = sb.tagify()
    assert isinstance(tagified, TagifiedTagList)
    sidebar, collapse = tagified
    assert isinstance(sidebar, TagifiedTag)
    assert isinstance(collapse, TagifiedTag)
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
    with pytest.raises(ValueError, match="`open` must be a string matching"):
        ui.sidebar(open="bad")  # pyright: ignore[reportArgumentType]

    with pytest.raises(ValueError, match="`open` must be one of"):
        ui.sidebar(open=("closed", "open"))  # pyright: ignore[reportArgumentType]

    with pytest.raises(ValueError, match="`desktop` must be one of"):
        ui.sidebar(open={"desktop": "bad"})  # pyright: ignore[reportArgumentType]

    with pytest.raises(TypeError, match="widescreen"):
        ui.sidebar(open={"widescreen": "open"})  # pyright: ignore[reportArgumentType]


def test_sidebar_resizable_attribute():
    sb_default, _ = get_sidebar_tags(ui.sidebar(open="open"))
    assert sb_default.attrs["data-resizable"] == ""

    sb_true, _ = get_sidebar_tags(ui.sidebar(open="open", resizable=True))
    assert sb_true.attrs["data-resizable"] == ""

    sb_false, _ = get_sidebar_tags(ui.sidebar(open="open", resizable=False))
    assert "data-resizable" not in sb_false.attrs


# Landmark roles ---------------------------------------------------------------------


def test_sidebar_neutral_markup_by_default():
    sidebar_tag, _ = get_sidebar_tags(ui.sidebar(id="sb"))

    assert sidebar_tag.name == "div"
    assert "role" not in sidebar_tag.attrs


def test_sidebar_complementary_role_uses_aside():
    sidebar_tag, _ = get_sidebar_tags(
        ui.sidebar(id="sb", title="Filters", role="complementary")
    )

    assert sidebar_tag.name == "aside"
    # <aside> is already a complementary landmark, so no explicit role
    assert "role" not in sidebar_tag.attrs


@pytest.mark.parametrize("role", ["form", "search", "region"])
def test_sidebar_landmark_roles_use_div_with_role(role: SidebarRole):
    sidebar_tag, _ = get_sidebar_tags(ui.sidebar(id="sb", title="Filters", role=role))

    assert sidebar_tag.name == "div"
    assert sidebar_tag.attrs["role"] == role


def test_sidebar_throws_for_invalid_role():
    with pytest.raises(ValueError, match="`role` must be one of"):
        ui.sidebar(role="navigation")  # pyright: ignore[reportArgumentType]


def test_sidebar_landmark_labels_from_title():
    html = TagList(ui.sidebar(id="sb", title="Filters", role="form")).render()["html"]

    assert 'aria-labelledby="sb-title"' in html
    assert '<header class="sidebar-title" id="sb-title">Filters</header>' in html


def test_sidebar_landmark_labels_from_title_without_sidebar_id():
    # With no sidebar `id`, the title id falls back to a random one
    html = TagList(ui.sidebar(title="Filters", role="form", open="always")).render()[
        "html"
    ]

    match = re.search(r'aria-labelledby="(bslib-sidebar-\d+-title)"', html)
    assert match is not None
    assert f'id="{match.group(1)}"' in html


def test_sidebar_landmark_uses_existing_title_id():
    html = TagList(
        ui.sidebar(
            id="sb",
            title=ui.tags.header("Filters", class_="sidebar-title", id="my-heading"),
            role="form",
        )
    ).render()["html"]

    assert 'aria-labelledby="my-heading"' in html


def test_sidebar_landmark_wraps_non_tag_title():
    html = TagList(
        ui.sidebar(id="sb", title=HTML("<b>Filters</b>"), role="form")
    ).render()["html"]

    assert 'aria-labelledby="sb-title"' in html
    assert '<div id="sb-title" style="display:contents"><b>Filters</b></div>' in html


def test_sidebar_landmark_hoists_aria_label():
    sidebar_tag, _ = get_sidebar_tags(
        ui.sidebar(id="sb", role="form", aria_label="Filters")
    )

    # The accessible name labels the landmark element (not the content div)
    assert sidebar_tag.attrs["aria-label"] == "Filters"
    assert "aria-labelledby" not in sidebar_tag.attrs

    html = TagList(ui.sidebar(id="sb", role="form", aria_label="Filters")).render()[
        "html"
    ]
    assert html.count('aria-label="Filters"') == 1


def test_sidebar_landmark_requires_accessible_name():
    with pytest.raises(ValueError, match="requires an accessible name"):
        ui.sidebar(id="sb", role="form").tagify()


def test_page_sidebar_places_layout_inside_main_landmark():
    html = TagList(
        ui.page_sidebar(ui.sidebar(id="sb", title="Filters"), "Main content")
    ).render()["html"]

    # The whole sidebar layout sits inside the page's <main> landmark, which
    # doesn't get gap spacing of its own (the layout provides it)
    main_start = html.index('<main class="bslib-page-main"')
    assert "bslib-gap-spacing" not in html[main_start : html.index(">", main_start)]
    assert main_start < html.index("bslib-sidebar-layout")
