"""Tests for shiny.ui._theme_presets module."""

from typing import get_args

from shiny.ui._theme_presets import (
    ShinyThemePreset,
    shiny_theme_presets,
    shiny_theme_presets_bootswatch,
    shiny_theme_presets_bundled,
)


class TestShinyThemePreset:
    """Tests for ShinyThemePreset literal type."""

    def test_shiny_theme_preset_is_literal(self):
        """ShinyThemePreset should be a Literal type."""
        allowed_values = get_args(ShinyThemePreset)
        assert isinstance(allowed_values, tuple)
        assert len(allowed_values) > 0

    def test_shiny_theme_preset_contains_bootstrap(self):
        """ShinyThemePreset should contain 'bootstrap'."""
        allowed_values = get_args(ShinyThemePreset)
        assert "bootstrap" in allowed_values

    def test_shiny_theme_preset_contains_shiny(self):
        """ShinyThemePreset should contain 'shiny'."""
        allowed_values = get_args(ShinyThemePreset)
        assert "shiny" in allowed_values

    def test_shiny_theme_preset_contains_bootswatch_themes(self):
        """ShinyThemePreset should contain bootswatch theme names."""
        allowed_values = get_args(ShinyThemePreset)
        bootswatch_themes = [
            "cerulean",
            "cosmo",
            "cyborg",
            "darkly",
            "flatly",
            "journal",
            "litera",
            "lumen",
            "lux",
            "materia",
            "minty",
            "morph",
            "pulse",
            "quartz",
            "sandstone",
            "simplex",
            "sketchy",
            "slate",
            "solar",
            "spacelab",
            "superhero",
            "united",
            "vapor",
            "yeti",
            "zephyr",
        ]
        for theme in bootswatch_themes:
            assert theme in allowed_values


class TestShinyThemePresetsTuple:
    """Tests for shiny_theme_presets tuple."""

    def test_shiny_theme_presets_is_tuple(self):
        """shiny_theme_presets should be a tuple."""
        assert isinstance(shiny_theme_presets, tuple)

    def test_shiny_theme_presets_contains_bootstrap(self):
        """shiny_theme_presets should contain 'bootstrap'."""
        assert "bootstrap" in shiny_theme_presets

    def test_shiny_theme_presets_contains_shiny(self):
        """shiny_theme_presets should contain 'shiny'."""
        assert "shiny" in shiny_theme_presets

    def test_shiny_theme_presets_matches_literal_type(self):
        """shiny_theme_presets tuple should contain same values as Literal type."""
        allowed_values = set(get_args(ShinyThemePreset))
        tuple_values = set(shiny_theme_presets)
        assert allowed_values == tuple_values


class TestShinyThemePresetsBundled:
    """Tests for shiny_theme_presets_bundled tuple."""

    def test_shiny_theme_presets_bundled_is_tuple(self):
        """shiny_theme_presets_bundled should be a tuple."""
        assert isinstance(shiny_theme_presets_bundled, tuple)

    def test_shiny_theme_presets_bundled_contains_bootstrap(self):
        """shiny_theme_presets_bundled should contain 'bootstrap'."""
        assert "bootstrap" in shiny_theme_presets_bundled

    def test_shiny_theme_presets_bundled_contains_shiny(self):
        """shiny_theme_presets_bundled should contain 'shiny'."""
        assert "shiny" in shiny_theme_presets_bundled

    def test_shiny_theme_presets_bundled_has_two_themes(self):
        """shiny_theme_presets_bundled should have exactly 2 themes."""
        assert len(shiny_theme_presets_bundled) == 2

    def test_shiny_theme_presets_bundled_subset_of_all_presets(self):
        """shiny_theme_presets_bundled should be a subset of shiny_theme_presets."""
        for theme in shiny_theme_presets_bundled:
            assert theme in shiny_theme_presets


class TestShinyThemePresetsBootswatch:
    """Tests for shiny_theme_presets_bootswatch tuple."""

    def test_shiny_theme_presets_bootswatch_is_tuple(self):
        """shiny_theme_presets_bootswatch should be a tuple."""
        assert isinstance(shiny_theme_presets_bootswatch, tuple)

    def test_shiny_theme_presets_bootswatch_does_not_contain_bundled(self):
        """shiny_theme_presets_bootswatch should not contain bundled themes."""
        for theme in shiny_theme_presets_bundled:
            assert theme not in shiny_theme_presets_bootswatch

    def test_shiny_theme_presets_bootswatch_subset_of_all_presets(self):
        """shiny_theme_presets_bootswatch should be a subset of shiny_theme_presets."""
        for theme in shiny_theme_presets_bootswatch:
            assert theme in shiny_theme_presets

    def test_bundled_plus_bootswatch_equals_all_presets(self):
        """Bundled plus bootswatch themes should equal all presets."""
        all_themes = set(shiny_theme_presets_bundled) | set(
            shiny_theme_presets_bootswatch
        )
        assert all_themes == set(shiny_theme_presets)
