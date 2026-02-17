"""Tests for shiny/ui/_theme.py - Theme class and related functions."""

import os
import tempfile
from pathlib import Path
from typing import Any, cast

import pytest

from shiny.ui._theme import (
    Theme,
    check_is_valid_preset,
    check_theme_pkg_installed,
    make_valid_path_str,
    path_pkg_preset,
    shiny_theme_presets,
)


# =============================================================================
# Tests for Theme class initialization
# =============================================================================
class TestThemeInit:
    def test_basic_init(self):
        """Test basic Theme initialization."""
        theme = Theme()
        assert theme._preset == "shiny"
        assert theme.name is None

    def test_init_with_preset(self):
        """Test Theme initialization with preset."""
        theme = Theme(preset="bootstrap")
        assert theme._preset == "bootstrap"

    def test_init_with_name(self):
        """Test Theme initialization with custom name."""
        theme = Theme(name="My Custom Theme")
        assert theme.name == "My Custom Theme"

    def test_init_with_invalid_preset_raises(self):
        """Test Theme initialization with invalid preset raises error."""
        with pytest.raises(ValueError, match="Invalid preset"):
            Theme(preset="not_a_preset")

    def test_init_with_include_paths_string(self):
        """Test Theme initialization with include_paths as string."""
        theme = Theme(include_paths="/some/path")
        assert "/some/path" in theme._include_paths

    def test_init_with_include_paths_path(self):
        """Test Theme initialization with include_paths as Path."""
        theme = Theme(include_paths=Path("/some/path"))
        assert "/some/path" in theme._include_paths

    def test_init_with_include_paths_list(self):
        """Test Theme initialization with include_paths as list."""
        theme = Theme(include_paths=["/path1", "/path2"])
        assert "/path1" in theme._include_paths
        assert "/path2" in theme._include_paths

    def test_init_empty_customizations(self):
        """Test Theme initialization has empty customizations."""
        theme = Theme()
        assert theme._uses == []
        assert theme._functions == []
        assert theme._defaults == []
        assert theme._mixins == []
        assert theme._rules == []


# =============================================================================
# Tests for Theme.preset property
# =============================================================================
class TestThemePreset:
    def test_preset_getter(self):
        """Test preset getter."""
        theme = Theme(preset="shiny")
        assert theme.preset == "shiny"

    def test_preset_setter_valid(self):
        """Test preset setter with valid value."""
        theme = Theme()
        theme.preset = "bootstrap"
        assert theme.preset == "bootstrap"

    def test_preset_setter_invalid_raises(self):
        """Test preset setter with invalid value raises error."""
        theme = Theme()
        with pytest.raises(ValueError, match="Invalid preset"):
            theme.preset = cast(Any, "invalid")

    def test_preset_setter_resets_css(self):
        """Test preset setter resets cached CSS."""
        theme = Theme()
        theme._css = "cached css"
        theme.preset = "bootstrap"
        assert theme._css == ""


# =============================================================================
# Tests for Theme.available_presets()
# =============================================================================
class TestAvailablePresets:
    def test_available_presets_returns_tuple(self):
        """Test available_presets returns a tuple."""
        presets = Theme.available_presets()
        assert isinstance(presets, tuple)

    def test_available_presets_contains_shiny(self):
        """Test available_presets contains 'shiny'."""
        presets = Theme.available_presets()
        assert "shiny" in presets

    def test_available_presets_contains_bootstrap(self):
        """Test available_presets contains 'bootstrap'."""
        presets = Theme.available_presets()
        assert "bootstrap" in presets


# =============================================================================
# Tests for Theme.add_uses()
# =============================================================================
class TestThemeAddUses:
    def test_add_uses_single(self):
        """Test adding single uses declaration."""
        theme = Theme()
        result = theme.add_uses("@use 'sass:math';")
        assert "@use 'sass:math';" in theme._uses
        assert result is theme  # Returns self for chaining

    def test_add_uses_multiple(self):
        """Test adding multiple uses declarations."""
        theme = Theme()
        theme.add_uses("@use 'sass:math';", "@use 'sass:color';")
        assert len(theme._uses) == 2

    def test_add_uses_resets_css(self):
        """Test add_uses resets cached CSS."""
        theme = Theme()
        theme._css = "cached"
        theme.add_uses("@use 'sass:math';")
        assert theme._css == ""


# =============================================================================
# Tests for Theme.add_functions()
# =============================================================================
class TestThemeAddFunctions:
    def test_add_functions_single(self):
        """Test adding single function."""
        theme = Theme()
        result = theme.add_functions("@function my-func() { @return 1; }")
        assert "@function my-func()" in theme._functions[0]
        assert result is theme

    def test_add_functions_multiple(self):
        """Test adding multiple functions."""
        theme = Theme()
        theme.add_functions("@function a() {}", "@function b() {}")
        assert len(theme._functions) == 2

    def test_add_functions_resets_css(self):
        """Test add_functions resets cached CSS."""
        theme = Theme()
        theme._css = "cached"
        theme.add_functions("@function f() {}")
        assert theme._css == ""


# =============================================================================
# Tests for Theme.add_defaults()
# =============================================================================
class TestThemeAddDefaults:
    def test_add_defaults_string(self):
        """Test adding defaults as string."""
        theme = Theme()
        result = theme.add_defaults("$primary: #007bff !default;")
        assert "$primary: #007bff !default;" in theme._defaults
        assert result is theme

    def test_add_defaults_kwargs(self):
        """Test adding defaults as kwargs."""
        theme = Theme()
        theme.add_defaults(primary_color="#ff0000")
        # Should convert underscore to kebab and add !default
        assert any("$primary-color: #ff0000 !default;" in d for d in theme._defaults)

    def test_add_defaults_bool_value(self):
        """Test adding defaults with boolean value."""
        theme = Theme()
        theme.add_defaults(enable_shadows=True)
        assert any("$enable-shadows: true !default;" in d for d in theme._defaults)

    def test_add_defaults_false_value(self):
        """Test adding defaults with False value."""
        theme = Theme()
        theme.add_defaults(enable_shadows=False)
        assert any("$enable-shadows: false !default;" in d for d in theme._defaults)

    def test_add_defaults_none_value(self):
        """Test adding defaults with None value."""
        theme = Theme()
        theme.add_defaults(some_var=None)
        assert any("$some-var: null !default;" in d for d in theme._defaults)

    def test_add_defaults_both_args_kwargs_raises(self):
        """Test adding defaults with both args and kwargs raises error."""
        theme = Theme()
        with pytest.raises(ValueError, match="Cannot provide both"):
            theme.add_defaults("$var: value;", another_var="value")

    def test_add_defaults_prepends(self):
        """Test defaults are prepended (not appended)."""
        theme = Theme()
        theme.add_defaults(first="1")
        theme.add_defaults(second="2")
        # Second should come before first (prepend behavior)
        first_idx = next(i for i, d in enumerate(theme._defaults) if "first" in d)
        second_idx = next(i for i, d in enumerate(theme._defaults) if "second" in d)
        assert second_idx < first_idx


# =============================================================================
# Tests for Theme.add_mixins()
# =============================================================================
class TestThemeAddMixins:
    def test_add_mixins_string(self):
        """Test adding mixins as string."""
        theme = Theme()
        result = theme.add_mixins("@mixin my-mixin { color: red; }")
        assert "@mixin my-mixin { color: red; }" in theme._mixins
        assert result is theme

    def test_add_mixins_kwargs(self):
        """Test adding mixins as kwargs."""
        theme = Theme()
        theme.add_mixins(headings_color="$primary")
        # Should convert underscore to kebab (no !default for mixins)
        assert any("$headings-color: $primary;" in m for m in theme._mixins)

    def test_add_mixins_multiple(self):
        """Test adding multiple mixins."""
        theme = Theme()
        theme.add_mixins("@mixin a {}", "@mixin b {}")
        assert len(theme._mixins) == 2


# =============================================================================
# Tests for Theme.add_rules()
# =============================================================================
class TestThemeAddRules:
    def test_add_rules_string(self):
        """Test adding rules as string."""
        theme = Theme()
        result = theme.add_rules(".my-class { color: blue; }")
        assert ".my-class { color: blue; }" in theme._rules
        assert result is theme

    def test_add_rules_kwargs(self):
        """Test adding rules as kwargs."""
        theme = Theme()
        theme.add_rules(custom_color="#123456")
        assert any("$custom-color: #123456;" in r for r in theme._rules)

    def test_add_rules_multiple(self):
        """Test adding multiple rules."""
        theme = Theme()
        theme.add_rules(".a {}", ".b {}")
        assert len(theme._rules) == 2


# =============================================================================
# Tests for Theme._has_customizations()
# =============================================================================
class TestThemeHasCustomizations:
    def test_no_customizations(self):
        """Test _has_customizations returns False when no customizations."""
        theme = Theme()
        assert theme._has_customizations() is False

    def test_has_functions(self):
        """Test _has_customizations returns True with functions."""
        theme = Theme()
        theme.add_functions("@function f() {}")
        assert theme._has_customizations() is True

    def test_has_defaults(self):
        """Test _has_customizations returns True with defaults."""
        theme = Theme()
        theme.add_defaults(color="red")
        assert theme._has_customizations() is True

    def test_has_mixins(self):
        """Test _has_customizations returns True with mixins."""
        theme = Theme()
        theme.add_mixins("@mixin m {}")
        assert theme._has_customizations() is True

    def test_has_rules(self):
        """Test _has_customizations returns True with rules."""
        theme = Theme()
        theme.add_rules(".rule {}")
        assert theme._has_customizations() is True


# =============================================================================
# Tests for Theme._can_use_precompiled()
# =============================================================================
class TestThemeCanUsePrecompiled:
    def test_can_use_precompiled_no_customizations(self):
        """Test _can_use_precompiled with no customizations."""
        theme = Theme(preset="shiny")
        assert theme._can_use_precompiled() is True

    def test_cannot_use_precompiled_with_customizations(self):
        """Test _can_use_precompiled with customizations."""
        theme = Theme(preset="shiny")
        theme.add_rules(".custom {}")
        assert theme._can_use_precompiled() is False


# =============================================================================
# Tests for Theme.to_sass()
# =============================================================================
class TestThemeToSass:
    def test_to_sass_returns_string(self):
        """Test to_sass returns a string."""
        theme = Theme()
        sass = theme.to_sass()
        assert isinstance(sass, str)

    def test_to_sass_includes_imports(self):
        """Test to_sass includes @import statements."""
        theme = Theme()
        sass = theme.to_sass()
        assert "@import" in sass

    def test_to_sass_includes_customizations(self):
        """Test to_sass includes customizations."""
        theme = Theme()
        theme.add_rules(".my-custom { color: red; }")
        sass = theme.to_sass()
        assert ".my-custom { color: red; }" in sass


# =============================================================================
# Tests for Theme.add_sass_layer_file()
# =============================================================================
class TestThemeAddSassLayerFile:
    def test_add_sass_layer_file_rules(self):
        """Test adding Sass layer file with rules."""
        theme = Theme()

        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.scss")
            with open(file_path, "w") as f:
                f.write("/*-- scss:rules --*/\n")
                f.write(".my-rule { color: red; }\n")

            theme.add_sass_layer_file(file_path)

        assert any(".my-rule { color: red; }" in r for r in theme._rules)

    def test_add_sass_layer_file_defaults(self):
        """Test adding Sass layer file with defaults."""
        theme = Theme()

        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.scss")
            with open(file_path, "w") as f:
                f.write("/*-- scss:defaults --*/\n")
                f.write("$my-var: red;\n")

            theme.add_sass_layer_file(file_path)

        assert any("$my-var: red;" in d for d in theme._defaults)

    def test_add_sass_layer_file_functions(self):
        """Test adding Sass layer file with functions."""
        theme = Theme()

        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.scss")
            with open(file_path, "w") as f:
                f.write("/*-- scss:functions --*/\n")
                f.write("@function my-func() { @return 1; }\n")

            theme.add_sass_layer_file(file_path)

        assert any("@function my-func()" in fn for fn in theme._functions)

    def test_add_sass_layer_file_mixins(self):
        """Test adding Sass layer file with mixins."""
        theme = Theme()

        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.scss")
            with open(file_path, "w") as f:
                f.write("/*-- scss:mixins --*/\n")
                f.write("@mixin my-mixin { color: blue; }\n")

            theme.add_sass_layer_file(file_path)

        assert any("@mixin my-mixin" in m for m in theme._mixins)

    def test_add_sass_layer_file_uses(self):
        """Test adding Sass layer file with uses."""
        theme = Theme()

        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.scss")
            with open(file_path, "w") as f:
                f.write("/*-- scss:uses --*/\n")
                f.write("@use 'sass:math';\n")

            theme.add_sass_layer_file(file_path)

        assert any("@use 'sass:math';" in u for u in theme._uses)

    def test_add_sass_layer_file_no_boundary_raises(self):
        """Test adding Sass file without boundary raises error."""
        theme = Theme()

        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.scss")
            with open(file_path, "w") as f:
                f.write("/* No boundary comments */\n")
                f.write(".some-rule { color: red; }\n")

            with pytest.raises(ValueError, match="doesn't contain at least one layer"):
                theme.add_sass_layer_file(file_path)


# =============================================================================
# Tests for Theme.tagify()
# =============================================================================
class TestThemeTagify:
    def test_tagify_raises(self):
        """Test tagify raises SyntaxError."""
        theme = Theme()
        with pytest.raises(SyntaxError, match="not meant to be used as a standalone"):
            theme.tagify()


# =============================================================================
# Tests for Theme method chaining
# =============================================================================
class TestThemeChaining:
    def test_method_chaining(self):
        """Test theme methods can be chained."""
        theme = (
            Theme("shiny")
            .add_defaults(primary="#ff0000")
            .add_mixins("@mixin m {}")
            .add_rules(".r {}")
        )

        assert any("primary" in d for d in theme._defaults)
        assert len(theme._mixins) == 1
        assert len(theme._rules) == 1


# =============================================================================
# Tests for check_is_valid_preset()
# =============================================================================
class TestCheckIsValidPreset:
    def test_valid_preset_shiny(self):
        """Test valid preset 'shiny'."""
        result = check_is_valid_preset("shiny")
        assert result == "shiny"

    def test_valid_preset_bootstrap(self):
        """Test valid preset 'bootstrap'."""
        result = check_is_valid_preset("bootstrap")
        assert result == "bootstrap"

    def test_invalid_preset_raises(self):
        """Test invalid preset raises error."""
        with pytest.raises(ValueError, match="Invalid preset"):
            check_is_valid_preset("not_valid")


# =============================================================================
# Tests for check_theme_pkg_installed()
# =============================================================================
class TestCheckThemePkgInstalled:
    def test_installed_package(self):
        """Test checking installed package doesn't raise."""
        # 'os' is always available
        check_theme_pkg_installed("os")

    def test_not_installed_package_raises(self):
        """Test checking non-installed package raises ImportError."""
        with pytest.raises(ImportError, match="required to compile"):
            check_theme_pkg_installed("nonexistent_package_xyz_123")


# =============================================================================
# Tests for make_valid_path_str()
# =============================================================================
class TestMakeValidPathStr:
    def test_simple_string(self):
        """Test simple string is unchanged."""
        result = make_valid_path_str("my-theme")
        assert result == "my-theme"

    def test_removes_invalid_chars(self):
        """Test invalid characters are replaced with dash."""
        result = make_valid_path_str("my theme!")
        assert result == "my-theme-"

    def test_lowercase(self):
        """Test result is lowercase."""
        result = make_valid_path_str("MyTheme")
        assert result == "mytheme"

    def test_multiple_special_chars(self):
        """Test multiple special characters become single dash."""
        result = make_valid_path_str("my@#$theme")
        assert result == "my-theme"


# =============================================================================
# Tests for path_pkg_preset()
# =============================================================================
class TestPathPkgPreset:
    def test_returns_string(self):
        """Test path_pkg_preset returns a string."""
        result = path_pkg_preset("shiny", "bootstrap.min.css")
        assert isinstance(result, str)

    def test_includes_preset(self):
        """Test path includes preset name."""
        result = path_pkg_preset("shiny", "test.css")
        assert "shiny" in result


# =============================================================================
# Tests for shiny_theme_presets constant
# =============================================================================
class TestShinyThemePresets:
    def test_is_tuple(self):
        """Test shiny_theme_presets is a tuple."""
        assert isinstance(shiny_theme_presets, tuple)

    def test_contains_shiny(self):
        """Test contains 'shiny' preset."""
        assert "shiny" in shiny_theme_presets

    def test_contains_bootstrap(self):
        """Test contains 'bootstrap' preset."""
        assert "bootstrap" in shiny_theme_presets


# =============================================================================
# Tests for Theme._combine_args_kwargs()
# =============================================================================
class TestCombineArgsKwargs:
    def test_args_only(self):
        """Test combining with args only."""
        result = Theme._combine_args_kwargs("line1", "line2", kwargs={})
        assert len(result) == 2

    def test_kwargs_only(self):
        """Test combining with kwargs only."""
        result = Theme._combine_args_kwargs(kwargs={"color": "red"}, is_default=False)
        assert any("$color: red;" in r for r in result)

    def test_kwargs_with_default(self):
        """Test combining kwargs with !default."""
        result = Theme._combine_args_kwargs(kwargs={"color": "red"}, is_default=True)
        assert any("$color: red !default;" in r for r in result)

    def test_empty_returns_empty(self):
        """Test empty args and kwargs returns empty list."""
        result = Theme._combine_args_kwargs(kwargs={})
        assert result == []
