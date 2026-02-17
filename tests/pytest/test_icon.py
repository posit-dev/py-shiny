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


def test_icon_bs_id_attribute():
    """Test that id attribute works for Bootstrap icons"""
    icon = ui.icon("star", lib="bs", id="my-star-icon")
    assert icon.attrs.get("id") == "my-star-icon"


# ============================================================================
# icon() tests - FontAwesome (without faicons installed)
# ============================================================================
def test_icon_fa_requires_faicons(monkeypatch):
    # Test that ImportError is raised when faicons is not available
    # We need to both remove from sys.modules and block the import
    import builtins
    import sys

    # Remove faicons from sys.modules
    monkeypatch.delitem(sys.modules, "faicons", raising=False)

    # Mock the import to raise ImportError when faicons is imported
    original_import = builtins.__import__

    def mock_import(name, *args, **kwargs):
        if name == "faicons":
            raise ImportError("No module named 'faicons'")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", mock_import)

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


# ============================================================================
# icon() tests - Bootstrap Icons styling parameters
# ============================================================================
def test_icon_bs_custom_fill():
    """Test that custom fill color works for Bootstrap icons"""
    icon = ui.icon("star", lib="bs", fill="red")
    style_attr = icon.attrs.get("style", "")
    assert "fill:red" in style_attr


def test_icon_bs_stroke_params():
    """Test that stroke parameters work for Bootstrap icons"""
    icon = ui.icon("star", lib="bs", stroke="blue", stroke_width="2")
    style_attr = icon.attrs.get("style", "")
    assert "stroke:blue" in style_attr
    assert "stroke-width:2" in style_attr


def test_icon_bs_additional_style():
    """Test that additional CSS styles can be passed for Bootstrap icons"""
    icon = ui.icon("star", lib="bs", style="opacity: 0.5")  # type: ignore[arg-type]
    style_attr = icon.attrs.get("style", "")
    assert "fill:currentColor" in style_attr
    assert "opacity: 0.5" in style_attr


# ============================================================================
# icon() tests - Examples from docstring
# ============================================================================
def test_icon_example_default_fa():
    """Test example: ui.icon('star')"""
    try:
        import faicons  # noqa: F401
    except ImportError:
        pytest.skip("faicons not installed")

    icon = ui.icon("star")
    assert isinstance(icon, Tag)
    # Should use FontAwesome by default
    rendered = str(icon)
    assert "fa" in rendered


def test_icon_example_bootstrap():
    """Test example: ui.icon('heart-fill', lib='bs')"""
    icon = ui.icon("heart-fill", lib="bs")
    assert isinstance(icon, Tag)
    assert icon.has_class("bi")
    assert icon.has_class("bi-heart-fill")


def test_icon_example_fa_style():
    """Test example: ui.icon('github', style='brands')"""
    try:
        import faicons  # noqa: F401
    except ImportError:
        pytest.skip("faicons not installed")

    icon = ui.icon("github", style="brands")
    assert isinstance(icon, Tag)


def test_icon_example_custom_size():
    """Test example: ui.icon('gear', size='2em')"""
    try:
        import faicons  # noqa: F401
    except ImportError:
        pytest.skip("faicons not installed")

    icon = ui.icon("gear", size="2em")
    assert isinstance(icon, Tag)


def test_icon_example_semantic():
    """Test example: ui.icon('circle-exclamation', title='Warning icon', a11y='semantic')"""
    try:
        import faicons  # noqa: F401
    except ImportError:
        pytest.skip("faicons not installed")

    icon = ui.icon("circle-exclamation", title="Warning icon", a11y="semantic")
    assert isinstance(icon, Tag)
    rendered = str(icon)
    assert "Warning icon" in rendered


def test_icon_example_custom_fill():
    """Test example: ui.icon('star', fill='gold')"""
    try:
        import faicons  # noqa: F401
    except ImportError:
        pytest.skip("faicons not installed")

    icon = ui.icon("star", fill="gold")
    assert isinstance(icon, Tag)


def test_icon_example_with_id():
    """Test example: ui.icon('star', id='my-icon')"""
    try:
        import faicons  # noqa: F401
    except ImportError:
        pytest.skip("faicons not installed")

    icon = ui.icon("star", id="my-icon")
    assert isinstance(icon, Tag)
    assert icon.attrs.get("id") == "my-icon"


# ============================================================================
# icon(lib="fa") equivalency tests with icon_svg()
# ============================================================================
def test_icon_fa_equivalent_to_icon_svg_basic():
    """Test that ui.icon() produces identical output to icon_svg() for basic usage"""
    try:
        from faicons import icon_svg
    except ImportError:
        pytest.skip("faicons not installed")

    icon1 = ui.icon("star", lib="fa")
    icon2 = icon_svg("star")

    html1 = str(icon1)
    html2 = str(icon2)

    assert html1 == html2


def test_icon_fa_equivalent_to_icon_svg_with_style():
    """Test equivalency with FontAwesome style parameter"""
    try:
        from faicons import icon_svg
    except ImportError:
        pytest.skip("faicons not installed")

    icon1 = ui.icon("github", lib="fa", style="brands")
    icon2 = icon_svg("github", style="brands")

    assert str(icon1) == str(icon2)


def test_icon_fa_equivalent_to_icon_svg_with_size():
    """Test equivalency with size parameter"""
    try:
        from faicons import icon_svg
    except ImportError:
        pytest.skip("faicons not installed")

    icon1 = ui.icon("star", lib="fa", size="2em")
    icon2 = icon_svg("star", height="2em", width="2em")

    assert str(icon1) == str(icon2)


def test_icon_fa_equivalent_to_icon_svg_with_title():
    """Test equivalency with title parameter"""
    try:
        from faicons import icon_svg
    except ImportError:
        pytest.skip("faicons not installed")

    icon1 = ui.icon("star", lib="fa", title="Favorite")
    icon2 = icon_svg("star", title="Favorite")

    assert str(icon1) == str(icon2)


def test_icon_fa_equivalent_to_icon_svg_semantic():
    """Test equivalency with semantic accessibility"""
    try:
        from faicons import icon_svg
    except ImportError:
        pytest.skip("faicons not installed")

    icon1 = ui.icon("circle-exclamation", lib="fa", title="Warning", a11y="semantic")
    icon2 = icon_svg("circle-exclamation", title="Warning", a11y="sem")

    assert str(icon1) == str(icon2)


def test_icon_fa_equivalent_to_icon_svg_decorative():
    """Test equivalency with decorative accessibility (default)"""
    try:
        from faicons import icon_svg
    except ImportError:
        pytest.skip("faicons not installed")

    icon1 = ui.icon("star", lib="fa", a11y="decorative")
    icon2 = icon_svg("star", a11y="deco")

    assert str(icon1) == str(icon2)


def test_icon_fa_with_id_attribute():
    """Test that icon() supports id attribute (enhancement over icon_svg)"""
    try:
        import faicons  # noqa: F401
    except ImportError:
        pytest.skip("faicons not installed")

    # icon() supports id attribute, which icon_svg() does not
    icon = ui.icon("star", lib="fa", id="star-icon")
    assert isinstance(icon, Tag)
    assert icon.attrs.get("id") == "star-icon"


def test_icon_fa_equivalent_to_icon_svg_default_fill():
    """Test that fill defaults to currentColor"""
    try:
        from faicons import icon_svg
    except ImportError:
        pytest.skip("faicons not installed")

    icon1 = ui.icon("star", lib="fa")
    icon2 = icon_svg("star", fill="currentColor")

    assert str(icon1) == str(icon2)


def test_icon_fa_equivalent_to_icon_svg_default_margins():
    """Test that margins default to icon_svg() defaults"""
    try:
        from faicons import icon_svg
    except ImportError:
        pytest.skip("faicons not installed")

    icon1 = ui.icon("star", lib="fa")
    icon2 = icon_svg("star", margin_left="auto", margin_right="0.2em")

    assert str(icon1) == str(icon2)


def test_icon_fa_equivalent_to_icon_svg_default_position():
    """Test that position defaults to relative"""
    try:
        from faicons import icon_svg
    except ImportError:
        pytest.skip("faicons not installed")

    icon1 = ui.icon("star", lib="fa")
    icon2 = icon_svg("star", position="relative")

    assert str(icon1) == str(icon2)


def test_icon_fa_equivalent_to_icon_svg_all_defaults():
    """Test that all defaults match icon_svg()"""
    try:
        from faicons import icon_svg
    except ImportError:
        pytest.skip("faicons not installed")

    icon1 = ui.icon("star", lib="fa")
    icon2 = icon_svg(
        "star",
        fill="currentColor",
        margin_left="auto",
        margin_right="0.2em",
        position="relative",
    )

    assert str(icon1) == str(icon2)


def test_icon_fa_equivalent_to_icon_svg_override_fill():
    """Test that fill can be overridden"""
    try:
        from faicons import icon_svg
    except ImportError:
        pytest.skip("faicons not installed")

    icon1 = ui.icon("star", lib="fa", fill="red")
    icon2 = icon_svg("star", fill="red")

    assert str(icon1) == str(icon2)


def test_icon_fa_equivalent_to_icon_svg_override_margins():
    """Test that margins can be overridden"""
    try:
        from faicons import icon_svg
    except ImportError:
        pytest.skip("faicons not installed")

    icon1 = ui.icon("star", lib="fa", margin_left="0", margin_right="1em")
    icon2 = icon_svg("star", margin_left="0", margin_right="1em")

    assert str(icon1) == str(icon2)


def test_icon_fa_equivalent_to_icon_svg_complex():
    """Test equivalency with complex combination of parameters"""
    try:
        from faicons import icon_svg
    except ImportError:
        pytest.skip("faicons not installed")

    # Test with parameters that both functions support
    icon1 = ui.icon(
        "github",
        lib="fa",
        style="brands",
        size="3rem",
        title="GitHub",
        a11y="semantic",
        fill="black",
        margin_left="0.5em",
    )
    icon2 = icon_svg(
        "github",
        style="brands",
        height="3rem",
        width="3rem",
        title="GitHub",
        a11y="sem",
        fill="black",
        margin_left="0.5em",
    )

    assert str(icon1) == str(icon2)


# ============================================================================
# Additional comprehensive parameter tests
# ============================================================================
def test_icon_fa_all_stroke_params():
    """Test all stroke-related parameters for FA icons"""
    try:
        from faicons import icon_svg
    except ImportError:
        pytest.skip("faicons not installed")

    icon1 = ui.icon(
        "star",
        lib="fa",
        stroke="red",
        stroke_width="2",
        stroke_opacity="0.5",
    )
    icon2 = icon_svg(
        "star",
        stroke="red",
        stroke_width="2",
        stroke_opacity="0.5",
    )

    assert str(icon1) == str(icon2)


def test_icon_fa_all_fill_params():
    """Test all fill-related parameters for FA icons"""
    try:
        from faicons import icon_svg
    except ImportError:
        pytest.skip("faicons not installed")

    icon1 = ui.icon(
        "star",
        lib="fa",
        fill="blue",
        fill_opacity="0.8",
    )
    icon2 = icon_svg(
        "star",
        fill="blue",
        fill_opacity="0.8",
    )

    assert str(icon1) == str(icon2)


def test_icon_bs_all_fill_and_stroke():
    """Test all fill and stroke parameters for Bootstrap icons"""
    icon = ui.icon(
        "star",
        lib="bs",
        fill="purple",
        fill_opacity="0.7",
        stroke="orange",
        stroke_width="3",
        stroke_opacity="0.9",
    )
    style = icon.attrs.get("style", "")
    assert "fill:purple" in style
    assert "fill-opacity:0.7" in style
    assert "stroke:orange" in style
    assert "stroke-width:3" in style
    assert "stroke-opacity:0.9" in style


def test_icon_bs_default_fill_not_overridden():
    """Test that default fill is used when no fill specified for BS"""
    icon = ui.icon("star", lib="bs")
    style = icon.attrs.get("style", "")
    assert "fill:currentColor" in style


def test_icon_bs_size_and_fill_together():
    """Test that size and fill work together for Bootstrap icons"""
    icon = ui.icon("star", lib="bs", size="3em", fill="green")
    style = icon.attrs.get("style", "")
    assert "height:3em" in style
    assert "width:3em" in style
    assert "fill:green" in style


def test_icon_bs_all_params_together():
    """Test all Bootstrap icon parameters together"""
    icon = ui.icon(
        "gear",
        lib="bs",
        size="2rem",
        fill="red",
        fill_opacity="0.5",
        stroke="blue",
        stroke_width="1",
        stroke_opacity="0.8",
        style="opacity: 0.9",  # type: ignore[arg-type]
        title="Settings",
        a11y="semantic",
        id="settings-icon",
    )

    # Check all attributes are present
    assert icon.attrs.get("id") == "settings-icon"
    assert icon.attrs.get("role") == "img"
    assert icon.attrs.get("aria-hidden") is None  # semantic, so not hidden

    style = icon.attrs.get("style", "")
    assert "fill:red" in style
    assert "fill-opacity:0.5" in style
    assert "stroke:blue" in style
    assert "stroke-width:1" in style
    assert "stroke-opacity:0.8" in style
    assert "height:2rem" in style
    assert "width:2rem" in style
    assert "opacity: 0.9" in style

    # Check title
    rendered = str(icon)
    assert "<title>Settings</title>" in rendered


def test_icon_fa_all_params_together():
    """Test all FontAwesome icon parameters together"""
    try:
        from faicons import icon_svg
    except ImportError:
        pytest.skip("faicons not installed")

    # Test without id first for exact equivalency
    icon1_no_id = ui.icon(
        "github",
        lib="fa",
        style="brands",
        fill="black",
        fill_opacity="0.9",
        stroke="white",
        stroke_width="0.5",
        stroke_opacity="0.3",
        size="2.5em",
        margin_left="1em",
        margin_right="1em",
        position="absolute",
        title="GitHub Logo",
        a11y="semantic",
    )

    icon2 = icon_svg(
        "github",
        style="brands",
        fill="black",
        fill_opacity="0.9",
        stroke="white",
        stroke_width="0.5",
        stroke_opacity="0.3",
        height="2.5em",
        width="2.5em",
        margin_left="1em",
        margin_right="1em",
        position="absolute",
        title="GitHub Logo",
        a11y="sem",
    )

    # Should be identical
    assert str(icon1_no_id) == str(icon2)

    # Now test with id (enhancement over icon_svg)
    icon1_with_id = ui.icon(
        "github",
        lib="fa",
        style="brands",
        fill="black",
        fill_opacity="0.9",
        size="2.5em",
        title="GitHub Logo",
        a11y="semantic",
        id="github-icon",
    )

    assert icon1_with_id.attrs.get("id") == "github-icon"


def test_icon_fa_none_values_use_defaults():
    """Test that None values trigger defaults for FA icons"""
    try:
        from faicons import icon_svg
    except ImportError:
        pytest.skip("faicons not installed")

    # Explicitly pass None for parameters with defaults
    icon1 = ui.icon(
        "star",
        lib="fa",
        fill=None,
        margin_left=None,
        margin_right=None,
        position=None,
    )

    # Should get same result as icon_svg with defaults
    icon2 = icon_svg("star")

    assert str(icon1) == str(icon2)


def test_icon_bs_numeric_size():
    """Test that numeric size works for Bootstrap icons"""
    icon = ui.icon("star", lib="bs", size=48)
    style = icon.attrs.get("style", "")
    assert "height:48" in style
    assert "width:48" in style


def test_icon_fa_numeric_size():
    """Test that numeric size works for FontAwesome icons"""
    try:
        from faicons import icon_svg
    except ImportError:
        pytest.skip("faicons not installed")

    icon1 = ui.icon("star", lib="fa", size=32)
    # as_css_unit(32) converts to "32.000000px"
    icon2 = icon_svg("star", height="32.000000px", width="32.000000px")

    assert str(icon1) == str(icon2)


def test_icon_bs_id_and_title():
    """Test id and title together for Bootstrap icons"""
    icon = ui.icon("star", lib="bs", id="my-star", title="Favorite")
    assert icon.attrs.get("id") == "my-star"
    rendered = str(icon)
    assert "<title>Favorite</title>" in rendered


def test_icon_fa_id_only():
    """Test that id can be set independently for FA icons"""
    try:
        import faicons  # noqa: F401
    except ImportError:
        pytest.skip("faicons not installed")

    icon = ui.icon("star", lib="fa", id="unique-icon")
    assert icon.attrs.get("id") == "unique-icon"
    # Should still have all the defaults
    rendered = str(icon)
    assert "currentColor" in rendered
    assert "margin-left:auto" in rendered
