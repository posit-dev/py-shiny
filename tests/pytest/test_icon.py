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
    assert "px" in style


def test_icon_bs_a11y_decorative():
    icon = ui.icon("star", lib="bs", a11y="decorative")
    assert icon.attrs.get("aria-hidden") == "true"
    assert icon.attrs.get("role") == "img"


def test_icon_bs_a11y_semantic_with_title():
    icon = ui.icon("star", lib="bs", title="Favorite", a11y="semantic")
    assert icon.attrs.get("aria-hidden") is None
    assert icon.attrs.get("role") == "img"
    assert icon.attrs.get("aria-label") == "Favorite"
    rendered = str(icon)
    assert "<title>Favorite</title>" in rendered


def test_icon_bs_a11y_semantic_without_title_derives_label():
    import warnings
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        icon = ui.icon("heart-fill", lib="bs", a11y="semantic")
    assert icon.attrs.get("aria-hidden") is None
    assert icon.attrs.get("role") == "img"
    assert icon.attrs.get("aria-label") == "heart fill"
    assert len(w) == 1
    assert "heart fill" in str(w[0].message)


def test_icon_bs_defaults_to_decorative():
    icon = ui.icon("star", lib="bs")
    assert icon.attrs.get("aria-hidden") == "true"


def test_icon_bs_unknown_icon_raises():
    with pytest.raises(ValueError, match="Unknown Bootstrap icon"):
        ui.icon("not-a-real-icon-name", lib="bs")


def test_icon_bs_id_attribute():
    icon = ui.icon("star", lib="bs", id="my-star-icon")
    assert icon.attrs.get("id") == "my-star-icon"


# ============================================================================
# icon() tests - FontAwesome
# ============================================================================
def test_icon_fa_returns_tag():
    icon = ui.icon("star", lib="fa")
    assert isinstance(icon, Tag)


def test_icon_fa_has_correct_class():
    icon = ui.icon("star", lib="fa")
    assert icon.has_class("fa")


def test_icon_fa_defaults_to_decorative():
    icon = ui.icon("star", lib="fa")
    assert icon.attrs.get("aria-hidden") == "true"
    assert icon.attrs.get("role") == "img"


def test_icon_fa_variant_parameter():
    icon = ui.icon("github", lib="fa", variant="brands")
    assert isinstance(icon, Tag)


def test_icon_fa_invalid_variant_raises():
    with pytest.raises(ValueError, match="Variant .* not found"):
        ui.icon("star", lib="fa", variant="brands")


def test_icon_fa_unknown_icon_raises():
    with pytest.raises(ValueError, match="Unknown FontAwesome icon"):
        ui.icon("not-a-real-icon-name", lib="fa")


def test_icon_fa_size_parameter():
    icon = ui.icon("star", lib="fa", size="2em")
    assert isinstance(icon, Tag)
    rendered = str(icon)
    assert "height:2em" in rendered
    assert "width:2em" in rendered


def test_icon_fa_default_fill():
    icon = ui.icon("star", lib="fa")
    rendered = str(icon)
    assert "currentColor" in rendered


def test_icon_fa_custom_fill():
    icon = ui.icon("star", lib="fa", fill="red")
    rendered = str(icon)
    assert "fill:red" in rendered


def test_icon_fa_default_margins():
    icon = ui.icon("star", lib="fa")
    rendered = str(icon)
    assert "margin-left:auto" in rendered
    assert "margin-right:0.2em" in rendered


def test_icon_fa_default_position():
    icon = ui.icon("star", lib="fa")
    rendered = str(icon)
    assert "position:relative" in rendered


def test_icon_fa_id_attribute():
    icon = ui.icon("star", lib="fa", id="star-icon")
    assert icon.attrs.get("id") == "star-icon"


def test_icon_fa_title():
    icon = ui.icon("star", lib="fa", title="Favorite")
    rendered = str(icon)
    assert "<title>Favorite</title>" in rendered


def test_icon_fa_semantic_a11y():
    icon = ui.icon("circle-exclamation", lib="fa", title="Warning", a11y="semantic")
    assert icon.attrs.get("aria-hidden") is None
    assert icon.attrs.get("role") == "img"
    assert icon.attrs.get("aria-label") == "Warning"


def test_icon_fa_stroke_params():
    icon = ui.icon("star", lib="fa", stroke="red", stroke_width="2", stroke_opacity="0.5")
    rendered = str(icon)
    assert 'stroke="red"' in rendered
    assert 'stroke-width="2"' in rendered
    assert 'stroke-opacity="0.5"' in rendered


def test_icon_fa_fill_opacity():
    icon = ui.icon("star", lib="fa", fill="blue", fill_opacity="0.8")
    rendered = str(icon)
    assert "fill:blue" in rendered
    assert 'fill-opacity="0.8"' in rendered


def test_icon_fa_aspect_ratio():
    """FA icons compute width from aspect ratio when only height is given."""
    icon = ui.icon("star", lib="fa")
    rendered = str(icon)
    # star icon has width=576, so width should be round(576/512, 2) = 1.12em
    assert "width:1.12em" in rendered
    assert "height:1em" in rendered


def test_icon_fa_preserves_aspect_ratio_attr():
    """When both height and width are set, preserveAspectRatio='none'."""
    icon = ui.icon("star", lib="fa", size="2em")
    assert icon.attrs.get("preserveAspectRatio") == "none"


def test_icon_fa_all_params_together():
    icon = ui.icon(
        "github",
        lib="fa",
        variant="brands",
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
        id="github-icon",
    )

    assert icon.attrs.get("id") == "github-icon"
    assert icon.attrs.get("role") == "img"
    assert icon.attrs.get("aria-label") == "GitHub Logo"
    assert icon.attrs.get("aria-hidden") is None

    rendered = str(icon)
    assert "fill:black" in rendered
    assert 'fill-opacity="0.9"' in rendered
    assert 'stroke="white"' in rendered
    assert 'stroke-width="0.5"' in rendered
    assert 'stroke-opacity="0.3"' in rendered
    assert "height:2.5em" in rendered
    assert "width:2.5em" in rendered
    assert "margin-left:1em" in rendered
    assert "margin-right:1em" in rendered
    assert "position:absolute" in rendered
    assert "<title>GitHub Logo</title>" in rendered


# ============================================================================
# icon() tests - Invalid library
# ============================================================================
def test_icon_invalid_lib_raises():
    with pytest.raises(ValueError, match="Unknown icon library"):
        ui.icon("star", lib="invalid")  # type: ignore


# ============================================================================
# icon() tests - Bootstrap Icons styling parameters
# ============================================================================
def test_icon_bs_custom_fill():
    icon = ui.icon("star", lib="bs", fill="red")
    style_attr = icon.attrs.get("style", "")
    assert "fill:red" in style_attr


def test_icon_bs_stroke_params():
    icon = ui.icon("star", lib="bs", stroke="blue", stroke_width="2")
    rendered = str(icon)
    assert 'stroke="blue"' in rendered
    assert 'stroke-width="2"' in rendered


def test_icon_bs_additional_style():
    icon = ui.icon("star", lib="bs", style="opacity: 0.5")  # type: ignore[arg-type]
    style_attr = icon.attrs.get("style", "")
    assert "fill:currentColor" in style_attr
    assert "opacity: 0.5" in style_attr


# ============================================================================
# icon() tests - Examples from docstring
# ============================================================================
def test_icon_example_default_fa():
    icon = ui.icon("star")
    assert isinstance(icon, Tag)
    rendered = str(icon)
    assert "fa" in rendered


def test_icon_example_bootstrap():
    icon = ui.icon("heart-fill", lib="bs")
    assert isinstance(icon, Tag)
    assert icon.has_class("bi")
    assert icon.has_class("bi-heart-fill")


def test_icon_example_fa_variant():
    icon = ui.icon("github", variant="brands")
    assert isinstance(icon, Tag)


def test_icon_example_custom_size():
    icon = ui.icon("gear", size="2em")
    assert isinstance(icon, Tag)


def test_icon_example_semantic():
    icon = ui.icon("circle-exclamation", title="Warning icon", a11y="semantic")
    assert isinstance(icon, Tag)
    rendered = str(icon)
    assert "Warning icon" in rendered


def test_icon_example_custom_fill():
    icon = ui.icon("star", fill="gold")
    assert isinstance(icon, Tag)


def test_icon_example_with_id():
    icon = ui.icon("star", id="my-icon")
    assert isinstance(icon, Tag)
    assert icon.attrs.get("id") == "my-icon"


# ============================================================================
# icon() tests - Additional BS parameter tests
# ============================================================================
def test_icon_bs_all_fill_and_stroke():
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
    rendered = str(icon)
    assert 'fill-opacity="0.7"' in rendered
    assert 'stroke="orange"' in rendered
    assert 'stroke-width="3"' in rendered
    assert 'stroke-opacity="0.9"' in rendered


def test_icon_bs_default_fill_not_overridden():
    icon = ui.icon("star", lib="bs")
    style = icon.attrs.get("style", "")
    assert "fill:currentColor" in style


def test_icon_bs_size_and_fill_together():
    icon = ui.icon("star", lib="bs", size="3em", fill="green")
    style = icon.attrs.get("style", "")
    assert "height:3em" in style
    assert "width:3em" in style
    assert "fill:green" in style


def test_icon_bs_all_params_together():
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

    assert icon.attrs.get("id") == "settings-icon"
    assert icon.attrs.get("role") == "img"
    assert icon.attrs.get("aria-hidden") is None

    style = icon.attrs.get("style", "")
    assert "fill:red" in style
    assert "height:2rem" in style
    assert "width:2rem" in style
    assert "opacity: 0.9" in style

    rendered = str(icon)
    assert 'fill-opacity="0.5"' in rendered
    assert 'stroke="blue"' in rendered
    assert 'stroke-width="1"' in rendered
    assert 'stroke-opacity="0.8"' in rendered
    assert "<title>Settings</title>" in rendered


def test_icon_bs_numeric_size():
    icon = ui.icon("star", lib="bs", size=48)
    style = icon.attrs.get("style", "")
    assert "height:48" in style
    assert "width:48" in style
    assert "px" in style


def test_icon_bs_id_and_title():
    icon = ui.icon("star", lib="bs", id="my-star", title="Favorite")
    assert icon.attrs.get("id") == "my-star"
    rendered = str(icon)
    assert "<title>Favorite</title>" in rendered


# ============================================================================
# icon() tests - Semantic sizes
# ============================================================================
def test_icon_semantic_size_lg():
    icon = ui.icon("star", lib="bs", size="lg")
    style = icon.attrs.get("style", "")
    assert "height:1.25em" in style
    assert "width:1.25em" in style


def test_icon_semantic_size_2xl():
    icon = ui.icon("star", lib="bs", size="2xl")
    style = icon.attrs.get("style", "")
    assert "height:2em" in style
    assert "width:2em" in style


def test_icon_semantic_size_2xs():
    icon = ui.icon("star", lib="bs", size="2xs")
    style = icon.attrs.get("style", "")
    assert "height:0.625em" in style
    assert "width:0.625em" in style
