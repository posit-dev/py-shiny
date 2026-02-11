from __future__ import annotations

import pytest
from htmltools import Tag

from shiny import ui


# ============================================================================
# icon() tests - Bootstrap Icons
# ============================================================================
def test_icon_bs_returns_tag():
    icon = ui.icon("star", lib="bs")
    assert isinstance(icon, Tag)


def test_icon_bs_has_correct_classes():
    icon = ui.icon("gear", lib="bs")
    assert icon.has_class("bi")
    assert icon.has_class("bi-gear")


def test_icon_bs_has_correct_viewbox():
    icon = ui.icon("star", lib="bs")
    assert icon.attrs.get("viewBox") == "0 0 16 16"


def test_icon_bs_has_fill_current_color():
    icon = ui.icon("star", lib="bs")
    style = icon.attrs.get("style", "")
    assert "fill:currentColor" in style


def test_icon_bs_size_parameter():
    icon = ui.icon("star", lib="bs", size="2em")
    style = icon.attrs.get("style", "")
    assert "height:2em" in style
    assert "width:2em" in style


def test_icon_bs_size_numeric():
    icon = ui.icon("star", lib="bs", size=24)
    style = icon.attrs.get("style", "")
    assert "height:24" in style
    assert "width:24" in style


def test_icon_bs_a11y_decorative():
    icon = ui.icon("star", lib="bs", a11y="decorative")
    assert icon.attrs.get("aria-hidden") == "true"
    assert icon.attrs.get("role") == "img"


def test_icon_bs_a11y_semantic_with_title():
    icon = ui.icon("star", lib="bs", title="Favorite", a11y="semantic")
    assert icon.attrs.get("aria-hidden") is None
    assert icon.attrs.get("role") == "img"
    rendered = str(icon)
    assert "<title>Favorite</title>" in rendered


def test_icon_bs_a11y_semantic_requires_title():
    with pytest.raises(ValueError, match="title is required"):
        ui.icon("star", lib="bs", a11y="semantic")


def test_icon_bs_unknown_icon_raises():
    with pytest.raises(ValueError, match="Unknown Bootstrap icon"):
        ui.icon("not-a-real-icon-name", lib="bs")


def test_icon_bs_kwargs_passed_through():
    icon = ui.icon("star", lib="bs", class_="custom-class", data_foo="bar")
    assert icon.has_class("custom-class")
    assert icon.attrs.get("data-foo") == "bar"


# ============================================================================
# icon() tests - FontAwesome (without faicons installed)
# ============================================================================
def test_icon_fa_requires_faicons():
    # This test assumes faicons is not installed in the test environment
    # If faicons is installed, this test will be skipped
    try:
        import faicons  # noqa: F401

        pytest.skip("faicons is installed, skipping ImportError test")
    except ImportError:
        pass

    with pytest.raises(ImportError, match="pip install faicons"):
        ui.icon("star", lib="fa")


# ============================================================================
# icon() tests - Invalid library
# ============================================================================
def test_icon_invalid_lib_raises():
    with pytest.raises(ValueError, match="Unknown icon library"):
        ui.icon("star", lib="invalid")  # type: ignore


# ============================================================================
# icon() tests - FontAwesome (with faicons installed)
# ============================================================================
def test_icon_fa_with_faicons():
    try:
        import faicons  # noqa: F401
    except ImportError:
        pytest.skip("faicons not installed")

    icon = ui.icon("star", lib="fa")
    assert isinstance(icon, Tag)


def test_icon_fa_style_parameter():
    try:
        import faicons  # noqa: F401
    except ImportError:
        pytest.skip("faicons not installed")

    icon = ui.icon("github", lib="fa", style="brands")
    assert isinstance(icon, Tag)


def test_icon_fa_size_parameter():
    try:
        import faicons  # noqa: F401
    except ImportError:
        pytest.skip("faicons not installed")

    icon = ui.icon("star", lib="fa", size="2em")
    assert isinstance(icon, Tag)
