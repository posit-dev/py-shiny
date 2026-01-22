"""Tests for shiny.ui._theme_presets module."""

from shiny.ui._theme_presets import (
    shiny_theme_presets,
    shiny_theme_presets_bootswatch,
    shiny_theme_presets_bundled,
)


class TestThemePresets:
    """Tests for theme preset constants."""

    def test_shiny_theme_presets_is_tuple(self) -> None:
        """Test that shiny_theme_presets is a tuple."""
        assert isinstance(shiny_theme_presets, tuple)

    def test_shiny_theme_presets_not_empty(self) -> None:
        """Test that shiny_theme_presets is not empty."""
        assert len(shiny_theme_presets) > 0

    def test_shiny_theme_presets_contains_bootstrap(self) -> None:
        """Test that bootstrap is in presets."""
        assert "bootstrap" in shiny_theme_presets

    def test_shiny_theme_presets_contains_shiny(self) -> None:
        """Test that shiny is in presets."""
        assert "shiny" in shiny_theme_presets

    def test_shiny_theme_presets_bundled_is_tuple(self) -> None:
        """Test that bundled presets is a tuple."""
        assert isinstance(shiny_theme_presets_bundled, tuple)

    def test_shiny_theme_presets_bundled_contains_bootstrap(self) -> None:
        """Test that bundled presets contains bootstrap."""
        assert "bootstrap" in shiny_theme_presets_bundled

    def test_shiny_theme_presets_bundled_contains_shiny(self) -> None:
        """Test that bundled presets contains shiny."""
        assert "shiny" in shiny_theme_presets_bundled

    def test_shiny_theme_presets_bundled_has_two_items(self) -> None:
        """Test that bundled presets has exactly two items."""
        assert len(shiny_theme_presets_bundled) == 2

    def test_shiny_theme_presets_bootswatch_is_tuple(self) -> None:
        """Test that bootswatch presets is a tuple."""
        assert isinstance(shiny_theme_presets_bootswatch, tuple)

    def test_shiny_theme_presets_bootswatch_not_empty(self) -> None:
        """Test that bootswatch presets is not empty."""
        assert len(shiny_theme_presets_bootswatch) > 0

    def test_bootswatch_presets_not_in_bundled(self) -> None:
        """Test that bootswatch presets are not in bundled presets."""
        for preset in shiny_theme_presets_bootswatch:
            assert preset not in shiny_theme_presets_bundled

    def test_all_bootswatch_in_main_presets(self) -> None:
        """Test that all bootswatch presets are in main presets."""
        for preset in shiny_theme_presets_bootswatch:
            assert preset in shiny_theme_presets

    def test_all_bundled_in_main_presets(self) -> None:
        """Test that all bundled presets are in main presets."""
        for preset in shiny_theme_presets_bundled:
            assert preset in shiny_theme_presets

    def test_presets_all_strings(self) -> None:
        """Test that all presets are strings."""
        for preset in shiny_theme_presets:
            assert isinstance(preset, str)

    def test_presets_no_empty_strings(self) -> None:
        """Test that no presets are empty strings."""
        for preset in shiny_theme_presets:
            assert preset != ""
            assert len(preset) > 0

    def test_common_bootswatch_themes_present(self) -> None:
        """Test that common Bootswatch themes are present."""
        common_themes = [
            "cerulean",
            "cosmo",
            "cyborg",
            "darkly",
            "flatly",
            "journal",
        ]
        for theme in common_themes:
            assert theme in shiny_theme_presets_bootswatch

    def test_presets_unique(self) -> None:
        """Test that all presets are unique."""
        assert len(shiny_theme_presets) == len(set(shiny_theme_presets))

    def test_bootswatch_presets_unique(self) -> None:
        """Test that all bootswatch presets are unique."""
        assert len(shiny_theme_presets_bootswatch) == len(
            set(shiny_theme_presets_bootswatch)
        )

    def test_bundled_presets_unique(self) -> None:
        """Test that all bundled presets are unique."""
        assert len(shiny_theme_presets_bundled) == len(set(shiny_theme_presets_bundled))

    def test_presets_count_matches_bundled_plus_bootswatch(self) -> None:
        """Test that total presets equals bundled plus bootswatch."""
        assert len(shiny_theme_presets) == len(shiny_theme_presets_bundled) + len(
            shiny_theme_presets_bootswatch
        )

    def test_all_presets_lowercase(self) -> None:
        """Test that all presets are lowercase."""
        for preset in shiny_theme_presets:
            assert preset == preset.lower()
