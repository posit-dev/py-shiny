"""
Unit tests for shiny/ui/_theme_brand.py
Tests for BrandBootstrapConfigFromYaml, BrandBootstrapConfig, and ThemeBrand classes
"""

import warnings
from typing import Any, Callable
from unittest.mock import MagicMock, patch

import pytest

from shiny.ui._theme_brand import (
    BrandBootstrapConfig,
    BrandBootstrapConfigFromYaml,
    ThemeBrand,
    bootstrap_colors,
)


# =============================================================================
# Tests for bootstrap_colors constant
# =============================================================================
class TestBootstrapColors:
    """Tests for the bootstrap_colors list"""

    def test_is_list(self):
        """bootstrap_colors should be a list"""
        assert isinstance(bootstrap_colors, list)

    def test_contains_expected_colors(self):
        """bootstrap_colors should contain all Bootstrap named colors"""
        expected = [
            "white",
            "black",
            "blue",
            "indigo",
            "purple",
            "pink",
            "red",
            "orange",
            "yellow",
            "green",
            "teal",
            "cyan",
        ]
        assert bootstrap_colors == expected

    def test_all_strings(self):
        """All colors should be strings"""
        for color in bootstrap_colors:
            assert isinstance(color, str)


# =============================================================================
# Tests for BrandBootstrapConfigFromYaml
# =============================================================================
class TestBrandBootstrapConfigFromYaml:
    """Tests for BrandBootstrapConfigFromYaml class"""

    def test_init_minimal(self):
        """Test initialization with minimal parameters"""
        config = BrandBootstrapConfigFromYaml(path="test.path")
        assert config._path == "test.path"
        assert config.version is None
        assert config.preset is None
        assert config.functions is None
        assert config.defaults is None
        assert config.mixins is None
        assert config.rules is None

    def test_init_with_preset(self):
        """Test initialization with preset string"""
        config = BrandBootstrapConfigFromYaml(path="test.path", preset="shiny")
        assert config.preset == "shiny"

    def test_init_with_version(self):
        """Test initialization with version"""
        config = BrandBootstrapConfigFromYaml(path="test.path", version=5)
        assert config.version == 5

    def test_init_with_functions(self):
        """Test initialization with functions string"""
        config = BrandBootstrapConfigFromYaml(
            path="test.path", functions="@function test() { @return 1; }"
        )
        assert config.functions == "@function test() { @return 1; }"

    def test_init_with_mixins(self):
        """Test initialization with mixins string"""
        config = BrandBootstrapConfigFromYaml(
            path="test.path", mixins="@mixin test() { color: red; }"
        )
        assert config.mixins == "@mixin test() { color: red; }"

    def test_init_with_rules(self):
        """Test initialization with rules string"""
        config = BrandBootstrapConfigFromYaml(
            path="test.path", rules=".test { color: blue; }"
        )
        assert config.rules == ".test { color: blue; }"

    def test_init_with_defaults_dict(self):
        """Test initialization with defaults dictionary"""
        defaults = {"primary": "#007bff", "secondary": "#6c757d"}
        config = BrandBootstrapConfigFromYaml(path="test.path", defaults=defaults)
        assert config.defaults == defaults

    def test_init_with_all_params(self):
        """Test initialization with all parameters"""
        config = BrandBootstrapConfigFromYaml(
            path="test.path",
            version=5,
            preset="shiny",
            functions="@function test() {}",
            defaults={"primary": "#007bff"},
            mixins="@mixin test() {}",
            rules=".test {}",
        )
        assert config._path == "test.path"
        assert config.version == 5
        assert config.preset == "shiny"
        assert config.functions == "@function test() {}"
        assert config.defaults == {"primary": "#007bff"}
        assert config.mixins == "@mixin test() {}"
        assert config.rules == ".test {}"


class TestBrandBootstrapConfigFromYamlValidateStr:
    """Tests for _validate_str method"""

    def test_validate_str_none(self):
        """None should be valid"""
        config = BrandBootstrapConfigFromYaml(path="test", preset=None)
        assert config.preset is None

    def test_validate_str_string(self):
        """String should be valid"""
        config = BrandBootstrapConfigFromYaml(path="test", preset="shiny")
        assert config.preset == "shiny"

    def test_validate_str_invalid_int(self):
        """Integer should raise ValueError"""
        with pytest.raises(ValueError, match="Invalid brand.*preset.*Must be a string"):
            BrandBootstrapConfigFromYaml(path="test", preset=123)

    def test_validate_str_invalid_list(self):
        """List should raise ValueError"""
        with pytest.raises(
            ValueError, match="Invalid brand.*functions.*Must be a string"
        ):
            BrandBootstrapConfigFromYaml(path="test", functions=["func1", "func2"])


class TestBrandBootstrapConfigFromYamlValidateDefaults:
    """Tests for _validate_defaults method"""

    def test_validate_defaults_none(self):
        """None should be valid"""
        config = BrandBootstrapConfigFromYaml(path="test", defaults=None)
        assert config.defaults is None

    def test_validate_defaults_empty_dict(self):
        """Empty dict should be valid"""
        config = BrandBootstrapConfigFromYaml(path="test", defaults={})
        assert config.defaults == {}

    def test_validate_defaults_with_string_values(self):
        """Dict with string values should be valid"""
        config = BrandBootstrapConfigFromYaml(
            path="test", defaults={"color": "#fff", "name": "test"}
        )
        assert config.defaults == {"color": "#fff", "name": "test"}

    def test_validate_defaults_with_int_values(self):
        """Dict with int values should be valid"""
        config = BrandBootstrapConfigFromYaml(
            path="test", defaults={"size": 16, "count": 5}
        )
        assert config.defaults == {"size": 16, "count": 5}

    def test_validate_defaults_with_float_values(self):
        """Dict with float values should be valid"""
        config = BrandBootstrapConfigFromYaml(
            path="test", defaults={"ratio": 1.5, "scale": 0.75}
        )
        assert config.defaults == {"ratio": 1.5, "scale": 0.75}

    def test_validate_defaults_with_bool_values(self):
        """Dict with bool values should be valid"""
        config = BrandBootstrapConfigFromYaml(
            path="test", defaults={"enabled": True, "disabled": False}
        )
        assert config.defaults == {"enabled": True, "disabled": False}

    def test_validate_defaults_with_none_values(self):
        """Dict with None values should be valid"""
        config = BrandBootstrapConfigFromYaml(
            path="test", defaults={"empty": None, "present": "value"}
        )
        assert config.defaults == {"empty": None, "present": "value"}

    def test_validate_defaults_with_mixed_scalar_values(self):
        """Dict with mixed scalar values should be valid"""
        config = BrandBootstrapConfigFromYaml(
            path="test",
            defaults={
                "string": "test",
                "int": 42,
                "float": 3.14,
                "bool": True,
                "none": None,
            },
        )
        assert config.defaults == {
            "string": "test",
            "int": 42,
            "float": 3.14,
            "bool": True,
            "none": None,
        }

    def test_validate_defaults_invalid_not_dict(self):
        """Non-dict should raise ValueError"""
        with pytest.raises(ValueError, match="must be a dictionary"):
            BrandBootstrapConfigFromYaml(path="test", defaults="not a dict")

    def test_validate_defaults_invalid_list(self):
        """List should raise ValueError"""
        with pytest.raises(ValueError, match="must be a dictionary"):
            BrandBootstrapConfigFromYaml(path="test", defaults=["a", "b"])

    def test_validate_defaults_invalid_non_string_keys(self):
        """Dict with non-string keys should raise ValueError"""
        with pytest.raises(ValueError, match="all keys must be strings"):
            BrandBootstrapConfigFromYaml(path="test", defaults={123: "value"})

    def test_validate_defaults_invalid_non_scalar_values(self):
        """Dict with non-scalar values should raise ValueError"""
        with pytest.raises(ValueError, match="all values must be scalar"):
            BrandBootstrapConfigFromYaml(
                path="test", defaults={"key": ["list", "value"]}
            )

    def test_validate_defaults_invalid_nested_dict(self):
        """Dict with nested dict should raise ValueError"""
        with pytest.raises(ValueError, match="all values must be scalar"):
            BrandBootstrapConfigFromYaml(
                path="test", defaults={"key": {"nested": "dict"}}
            )


# =============================================================================
# Tests for BrandBootstrapConfig
# =============================================================================
class TestBrandBootstrapConfig:
    """Tests for BrandBootstrapConfig class"""

    def test_init_defaults(self):
        """Test initialization with default values"""
        config = BrandBootstrapConfig()
        # Version should be the major version
        assert config.version is not None
        assert config.preset is None
        assert config.functions is None
        assert config.defaults is None
        assert config.mixins is None
        assert config.rules is None

    def test_init_with_string_version(self):
        """Test initialization with string version"""
        config = BrandBootstrapConfig(version="5.3.0")
        assert config.version == "5"

    def test_init_with_int_version(self):
        """Test initialization with int version"""
        config = BrandBootstrapConfig(version=5)
        assert config.version == "5"

    def test_init_with_preset(self):
        """Test initialization with preset"""
        config = BrandBootstrapConfig(preset="shiny")
        assert config.preset == "shiny"

    def test_init_with_functions(self):
        """Test initialization with functions"""
        config = BrandBootstrapConfig(functions="@function test() {}")
        assert config.functions == "@function test() {}"

    def test_init_with_defaults(self):
        """Test initialization with defaults"""
        config = BrandBootstrapConfig(defaults={"primary": "#007bff"})
        assert config.defaults == {"primary": "#007bff"}

    def test_init_with_mixins(self):
        """Test initialization with mixins"""
        config = BrandBootstrapConfig(mixins="@mixin test() {}")
        assert config.mixins == "@mixin test() {}"

    def test_init_with_rules(self):
        """Test initialization with rules"""
        config = BrandBootstrapConfig(rules=".test { color: red; }")
        assert config.rules == ".test { color: red; }"

    def test_init_invalid_version_type(self):
        """Test that invalid version type raises ValueError"""
        with pytest.raises(ValueError, match="must be a string or integer"):
            BrandBootstrapConfig(version=["5"])  # type: ignore

    def test_init_invalid_version_type_dict(self):
        """Test that dict version type raises ValueError"""
        with pytest.raises(ValueError, match="must be a string or integer"):
            BrandBootstrapConfig(version={"version": 5})  # type: ignore

    def test_init_mismatched_major_version_warns(self):
        """Test that mismatched major version warns"""
        # This test depends on the current Bootstrap version being 5
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            _ = BrandBootstrapConfig(version="4.0.0")
            # Should warn about version mismatch
            assert len(w) >= 1
            assert "does not current support" in str(w[-1].message)


class TestBrandBootstrapConfigFromBrand:
    """Tests for from_brand class method"""

    def test_from_brand_no_defaults(self):
        """Test from_brand with brand that has no defaults"""
        brand = MagicMock()
        brand.defaults = None
        config = BrandBootstrapConfig.from_brand(brand)
        assert config.preset is None
        assert config.functions is None
        assert config.defaults is None
        assert config.mixins is None
        assert config.rules is None

    def test_from_brand_empty_defaults(self):
        """Test from_brand with brand that has empty defaults"""
        brand = MagicMock()
        brand.defaults = {}
        config = BrandBootstrapConfig.from_brand(brand)
        assert config.preset is None
        assert config.functions is None

    def test_from_brand_with_shiny_theme(self):
        """Test from_brand with shiny.theme in defaults"""
        brand = MagicMock()
        brand.defaults = {"shiny": {"theme": {"preset": "shiny", "rules": ".test {}"}}}
        config = BrandBootstrapConfig.from_brand(brand)
        assert config.preset == "shiny"
        assert config.rules == ".test {}"

    def test_from_brand_with_bootstrap(self):
        """Test from_brand with bootstrap in defaults"""
        brand = MagicMock()
        brand.defaults = {
            "bootstrap": {"preset": "bootstrap", "functions": "@function bs() {}"}
        }
        config = BrandBootstrapConfig.from_brand(brand)
        assert config.preset == "bootstrap"
        assert config.functions == "@function bs() {}"

    def test_from_brand_shiny_overrides_bootstrap_preset(self):
        """Test that shiny.theme.preset overrides bootstrap.preset"""
        brand = MagicMock()
        brand.defaults = {
            "bootstrap": {"preset": "bootstrap"},
            "shiny": {"theme": {"preset": "shiny"}},
        }
        config = BrandBootstrapConfig.from_brand(brand)
        assert config.preset == "shiny"

    def test_from_brand_joins_functions(self):
        """Test that functions from bootstrap and shiny are joined"""
        brand = MagicMock()
        brand.defaults = {
            "bootstrap": {"functions": "@function bs() {}"},
            "shiny": {"theme": {"functions": "@function shiny() {}"}},
        }
        config = BrandBootstrapConfig.from_brand(brand)
        assert config.functions is not None
        assert "@function bs() {}" in config.functions
        assert "@function shiny() {}" in config.functions

    def test_from_brand_joins_mixins(self):
        """Test that mixins from bootstrap and shiny are joined"""
        brand = MagicMock()
        brand.defaults = {
            "bootstrap": {"mixins": "@mixin bs() {}"},
            "shiny": {"theme": {"mixins": "@mixin shiny() {}"}},
        }
        config = BrandBootstrapConfig.from_brand(brand)
        assert config.mixins is not None
        assert "@mixin bs() {}" in config.mixins
        assert "@mixin shiny() {}" in config.mixins

    def test_from_brand_joins_rules(self):
        """Test that rules from bootstrap and shiny are joined"""
        brand = MagicMock()
        brand.defaults = {
            "bootstrap": {"rules": ".bs {}"},
            "shiny": {"theme": {"rules": ".shiny {}"}},
        }
        config = BrandBootstrapConfig.from_brand(brand)
        assert config.rules is not None
        assert ".bs {}" in config.rules
        assert ".shiny {}" in config.rules

    def test_from_brand_merges_defaults(self):
        """Test that defaults from bootstrap and shiny are merged"""
        brand = MagicMock()
        brand.defaults = {
            "bootstrap": {"defaults": {"bs-color": "blue"}},
            "shiny": {"theme": {"defaults": {"shiny-color": "red"}}},
        }
        config = BrandBootstrapConfig.from_brand(brand)
        assert config.defaults is not None
        assert config.defaults["bs-color"] == "blue"
        assert config.defaults["shiny-color"] == "red"

    def test_from_brand_shiny_defaults_override_bootstrap(self):
        """Test that shiny defaults override bootstrap defaults"""
        brand = MagicMock()
        brand.defaults = {
            "bootstrap": {"defaults": {"color": "blue"}},
            "shiny": {"theme": {"defaults": {"color": "red"}}},
        }
        config = BrandBootstrapConfig.from_brand(brand)
        assert config.defaults is not None
        assert config.defaults["color"] == "red"


# =============================================================================
# Tests for ThemeBrand
# =============================================================================
class TestThemeBrandGetThemeName:
    """Tests for _get_theme_name method"""

    def test_get_theme_name_no_meta(self):
        """Test _get_theme_name with no meta"""
        brand = MagicMock()
        brand.meta = None
        brand.defaults = None
        brand.color = None
        brand.typography = None

        theme = ThemeBrand.__new__(ThemeBrand)
        result = theme._get_theme_name(brand)
        assert result == "brand"

    def test_get_theme_name_no_name(self):
        """Test _get_theme_name with meta but no name"""
        brand = MagicMock()
        brand.meta = MagicMock()
        brand.meta.name = None
        brand.defaults = None
        brand.color = None
        brand.typography = None

        theme = ThemeBrand.__new__(ThemeBrand)
        result = theme._get_theme_name(brand)
        assert result == "brand"

    def test_get_theme_name_short_name(self):
        """Test _get_theme_name with short name"""
        brand = MagicMock()
        brand.meta = MagicMock()
        brand.meta.name = MagicMock()
        brand.meta.name.short = "ShortName"
        brand.meta.name.full = "Full Name"
        brand.defaults = None
        brand.color = None
        brand.typography = None

        theme = ThemeBrand.__new__(ThemeBrand)
        result = theme._get_theme_name(brand)
        assert result == "ShortName"

    def test_get_theme_name_full_name_no_short(self):
        """Test _get_theme_name with full name but no short"""
        brand = MagicMock()
        brand.meta = MagicMock()
        brand.meta.name = MagicMock()
        brand.meta.name.short = None
        brand.meta.name.full = "Full Name"
        brand.defaults = None
        brand.color = None
        brand.typography = None

        theme = ThemeBrand.__new__(ThemeBrand)
        result = theme._get_theme_name(brand)
        assert result == "Full Name"


class TestThemeBrandPrepareColorVars:
    """Tests for _prepare_color_vars static method"""

    def test_prepare_color_vars_no_color(self):
        """Test with no color defined"""
        brand = MagicMock()
        brand.color = None

        _palette_defaults, color_defaults, _rules = ThemeBrand._prepare_color_vars(
            brand
        )

        assert palette_defaults == {}
        assert color_defaults == {}
        assert rules == []

    def test_prepare_color_vars_with_theme_colors(self):
        """Test with theme colors defined"""
        brand = MagicMock()
        brand.color = MagicMock()

        def _to_dict(include: str) -> dict[str, str]:
            if include == "theme":
                return {"primary": "#007bff", "secondary": "#6c757d"}
            return {}

        brand.color.to_dict.side_effect = _to_dict

        palette_defaults, color_defaults, _rules = ThemeBrand._prepare_color_vars(brand)

        assert "brand_color_primary" in color_defaults
        assert color_defaults["brand_color_primary"] == "#007bff"
        assert "brand_color_secondary" in color_defaults
        assert color_defaults["brand_color_secondary"] == "#6c757d"

    def test_prepare_color_vars_with_palette_bootstrap_color(self):
        """Test with palette containing bootstrap color"""
        brand = MagicMock()
        brand.color = MagicMock()

        def _to_dict(include: str) -> dict[str, str]:
            if include == "theme":
                return {}
            return {"red": "#ff0000", "custom": "#123456"}

        brand.color.to_dict.side_effect = _to_dict

        palette_defaults, color_defaults, rules = ThemeBrand._prepare_color_vars(brand)

        # Bootstrap color 'red' should be in color_defaults
        assert color_defaults["red"] == "#ff0000"
        # Palette should have brand-prefixed vars
        assert palette_defaults["brand-red"] == "#ff0000"
        assert palette_defaults["brand-custom"] == "#123456"

    def test_prepare_color_vars_rules_structure(self):
        """Test that rules have correct structure"""
        brand = MagicMock()
        brand.color = MagicMock()

        def _to_dict(include: str) -> dict[str, str]:
            if include == "theme":
                return {}
            return {"mycolor": "#abcdef"}

        brand.color.to_dict.side_effect = _to_dict

        _, _, rules = ThemeBrand._prepare_color_vars(brand)

        assert len(rules) >= 4
        assert ":root {" in rules
        assert "}" in rules
        # Check for CSS variable
        assert any("--brand-mycolor" in rule for rule in rules)


class TestThemeBrandPrepareTypographyVars:
    """Tests for _prepare_typography_vars static method"""

    def test_prepare_typography_vars_no_typography(self):
        """Test with no typography defined"""
        brand = MagicMock()
        brand.typography = None

        result = ThemeBrand._prepare_typography_vars(brand)
        assert result == {}

    def test_prepare_typography_vars_with_data(self):
        """Test with typography data"""
        brand = MagicMock()
        brand.typography = MagicMock()
        brand.typography.model_dump.return_value = {
            "base": {"size": "16rem", "line-height": "1.5"},
            "heading": {"weight": "700"},
        }

        result = ThemeBrand._prepare_typography_vars(brand)

        assert "brand_typography_base_size" in result
        assert result["brand_typography_base_size"] == "16rem"
        assert "brand_typography_base_line-height" in result
        assert result["brand_typography_base_line-height"] == "1.5"
        assert "brand_typography_heading_weight" in result
        assert result["brand_typography_heading_weight"] == "700"

    def test_prepare_typography_vars_excludes_fonts(self):
        """Test that fonts are excluded from typography dump"""
        brand = MagicMock()
        brand.typography = MagicMock()
        brand.typography.model_dump.return_value = {}

        ThemeBrand._prepare_typography_vars(brand)

        # Verify model_dump was called with exclude={"fonts"}
        call_kwargs = brand.typography.model_dump.call_args[1]
        assert "fonts" in call_kwargs["exclude"]


class TestThemeBrandInit:
    """Tests for ThemeBrand initialization"""

    @patch.object(ThemeBrand, "add_sass_layer_file")
    @patch("shiny.ui._theme_brand.path_pkg_www")
    def test_init_basic(
        self, mock_path_pkg_www: MagicMock, mock_add_sass: MagicMock
    ) -> None:
        """Test basic initialization"""
        mock_path_pkg_www.return_value = "/mock/path/brand.scss"

        brand = MagicMock()
        brand.meta = None
        brand.defaults = None
        brand.color = None
        brand.typography = None

        theme = ThemeBrand(brand)

        assert theme.brand is brand
        assert theme.name == "brand"

    @patch.object(ThemeBrand, "add_sass_layer_file")
    @patch("shiny.ui._theme_brand.path_pkg_www")
    def test_init_with_include_paths(
        self, mock_path_pkg_www: MagicMock, mock_add_sass: MagicMock
    ) -> None:
        """Test initialization with include_paths"""
        mock_path_pkg_www.return_value = "/mock/path/brand.scss"

        brand = MagicMock()
        brand.meta = None
        brand.defaults = None
        brand.color = None
        brand.typography = None

        theme = ThemeBrand(brand, include_paths=["/custom/path"])

        assert theme.brand is brand

    @patch.object(ThemeBrand, "add_sass_layer_file")
    @patch("shiny.ui._theme_brand.path_pkg_www")
    def test_init_with_preset(
        self, mock_path_pkg_www: MagicMock, mock_add_sass: MagicMock
    ) -> None:
        """Test initialization with preset from brand"""
        mock_path_pkg_www.return_value = "/mock/path/brand.scss"

        brand = MagicMock()
        brand.meta = None
        brand.defaults = {"bootstrap": {"preset": "shiny"}}
        brand.color = None
        brand.typography = None

        theme = ThemeBrand(brand)

        assert theme.preset == "shiny"

    @patch.object(ThemeBrand, "add_sass_layer_file")
    @patch("shiny.ui._theme_brand.path_pkg_www")
    def test_init_with_colors(
        self, mock_path_pkg_www: MagicMock, mock_add_sass: MagicMock
    ) -> None:
        """Test initialization with colors"""
        mock_path_pkg_www.return_value = "/mock/path/brand.scss"

        brand = MagicMock()
        brand.meta = None
        brand.defaults = None
        brand.color = MagicMock()

        def _to_dict(include: str) -> dict[str, str]:
            if include == "theme":
                return {"primary": "#007bff"}
            return {}

        brand.color.to_dict.side_effect = _to_dict
        brand.typography = None

        theme = ThemeBrand(brand)

        # Theme should have been created with color defaults
        assert theme.brand is brand


class TestThemeBrandAddDefaultsHdr:
    """Tests for _add_defaults_hdr method"""

    @patch.object(ThemeBrand, "add_sass_layer_file")
    @patch("shiny.ui._theme_brand.path_pkg_www")
    def test_add_defaults_hdr(
        self, mock_path_pkg_www: MagicMock, mock_add_sass: MagicMock
    ) -> None:
        """Test _add_defaults_hdr adds header and values"""
        mock_path_pkg_www.return_value = "/mock/path/brand.scss"

        brand = MagicMock()
        brand.meta = None
        brand.defaults = None
        brand.color = None
        brand.typography = None

        theme = ThemeBrand(brand)

        # Clear any existing defaults to test _add_defaults_hdr
        theme._defaults = []
        theme._add_defaults_hdr("test header", primary="#007bff")

        # Check that header comment and values were added
        sass = "".join(str(d) for d in theme._defaults)
        assert "brand: test header" in sass
        assert "primary" in sass


class TestThemeBrandAddBrandBootstrapOther:
    """Tests for _add_brand_bootstrap_other method"""

    @patch.object(ThemeBrand, "add_sass_layer_file")
    @patch("shiny.ui._theme_brand.path_pkg_www")
    def test_add_brand_bootstrap_other_functions(
        self, mock_path_pkg_www: MagicMock, mock_add_sass: MagicMock
    ) -> None:
        """Test adding bootstrap functions"""
        mock_path_pkg_www.return_value = "/mock/path/brand.scss"

        brand = MagicMock()
        brand.meta = None
        brand.defaults = None
        brand.color = None
        brand.typography = None

        theme = ThemeBrand(brand)

        bootstrap_config = BrandBootstrapConfig(functions="@function test() {}")
        theme._add_brand_bootstrap_other(bootstrap_config)

        assert any("bootstrap.functions" in str(f) for f in theme._functions)

    @patch.object(ThemeBrand, "add_sass_layer_file")
    @patch("shiny.ui._theme_brand.path_pkg_www")
    def test_add_brand_bootstrap_other_mixins(
        self, mock_path_pkg_www: MagicMock, mock_add_sass: MagicMock
    ) -> None:
        """Test adding bootstrap mixins"""
        mock_path_pkg_www.return_value = "/mock/path/brand.scss"

        brand = MagicMock()
        brand.meta = None
        brand.defaults = None
        brand.color = None
        brand.typography = None

        theme = ThemeBrand(brand)

        bootstrap_config = BrandBootstrapConfig(mixins="@mixin test() {}")
        theme._add_brand_bootstrap_other(bootstrap_config)

        assert any("bootstrap.mixins" in str(m) for m in theme._mixins)

    @patch.object(ThemeBrand, "add_sass_layer_file")
    @patch("shiny.ui._theme_brand.path_pkg_www")
    def test_add_brand_bootstrap_other_rules(
        self, mock_path_pkg_www: MagicMock, mock_add_sass: MagicMock
    ) -> None:
        """Test adding bootstrap rules"""
        mock_path_pkg_www.return_value = "/mock/path/brand.scss"

        brand = MagicMock()
        brand.meta = None
        brand.defaults = None
        brand.color = None
        brand.typography = None

        theme = ThemeBrand(brand)

        bootstrap_config = BrandBootstrapConfig(rules=".test { color: red; }")
        theme._add_brand_bootstrap_other(bootstrap_config)

        assert any("bootstrap.rules" in str(r) for r in theme._rules)


class TestThemeBrandHtmlDependencies:
    """Tests for _html_dependencies method"""

    @patch.object(ThemeBrand, "add_sass_layer_file")
    @patch("shiny.ui._theme_brand.path_pkg_www")
    def test_html_dependencies_no_typography(
        self, mock_path_pkg_www: MagicMock, mock_add_sass: MagicMock
    ) -> None:
        """Test _html_dependencies with no typography"""
        mock_path_pkg_www.return_value = "/mock/path/brand.scss"

        brand = MagicMock()
        brand.meta = None
        brand.defaults = None
        brand.color = None
        brand.typography = None

        theme = ThemeBrand(brand)

        # Should return parent class dependencies
        deps = theme._html_dependencies()
        assert isinstance(deps, list)

    @patch.object(ThemeBrand, "add_sass_layer_file")
    @patch("shiny.ui._theme.Theme._html_dependencies")
    @patch.object(ThemeBrand, "_get_css_tempdir")
    @patch("shiny.ui._theme_brand.path_pkg_www")
    def test_html_dependencies_with_typography_no_fonts(
        self,
        mock_path_pkg_www: MagicMock,
        mock_tempdir: MagicMock,
        mock_parent_deps: MagicMock,
        mock_add_sass: MagicMock,
    ) -> None:
        """Test _html_dependencies with typography but no fonts dependency"""
        mock_path_pkg_www.return_value = "/mock/path/brand.scss"
        mock_tempdir.return_value = "/tmp/test"
        mock_parent_deps.return_value = []  # Mock parent class dependencies

        brand = MagicMock()
        brand.meta = None
        brand.defaults = None
        brand.color = None
        brand.typography = MagicMock()
        brand.typography.fonts_html_dependency.return_value = None

        theme = ThemeBrand(brand)

        deps = theme._html_dependencies()
        assert isinstance(deps, list)

    @patch.object(ThemeBrand, "add_sass_layer_file")
    @patch("shiny.ui._theme.Theme._html_dependencies")
    @patch("shiny.ui._theme_brand.Path")
    @patch.object(ThemeBrand, "_get_css_tempdir")
    @patch("shiny.ui._theme_brand.path_pkg_www")
    def test_html_dependencies_with_fonts_dependency(
        self,
        mock_path_pkg_www: MagicMock,
        mock_tempdir: MagicMock,
        mock_path_class: MagicMock,
        mock_parent_deps: MagicMock,
        mock_add_sass: MagicMock,
    ) -> None:
        """Test _html_dependencies with fonts dependency"""
        mock_path_pkg_www.return_value = "/mock/path/brand.scss"
        mock_tempdir.return_value = "/tmp/test"
        mock_parent_deps.return_value = []  # Mock parent class dependencies

        mock_path_instance = MagicMock()
        mock_path_class.return_value = mock_path_instance
        mock_path_instance.__truediv__ = MagicMock(return_value=mock_path_instance)

        brand = MagicMock()
        brand.meta = None
        brand.defaults = None
        brand.color = None
        brand.typography = MagicMock()

        mock_font_dep = MagicMock()
        brand.typography.fonts_html_dependency.return_value = mock_font_dep

        theme = ThemeBrand(brand)

        deps = theme._html_dependencies()

        # Should include font dependency
        assert mock_font_dep in deps
