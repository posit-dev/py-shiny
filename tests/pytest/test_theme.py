import re
import tempfile
from typing import Callable, Optional

import pytest
from htmltools import Tag

from shiny import App
from shiny.ui import (
    Theme,
    input_dark_mode,
    input_date_range,
    input_selectize,
    input_slider,
    page_bootstrap,
    page_fillable,
    page_sidebar,
    sidebar,
)
from shiny.ui._theme import (
    ShinyThemePreset,
    shiny_theme_presets,
    shiny_theme_presets_bundled,
)

from ._utils import skip_on_windows


def test_theme_stores_values_correctly():
    theme = (
        Theme("shiny")
        .add_defaults(
            headings_color="red",
            bar_color="purple",
            select_color_text="green",
            bslib_dashboard_design=True,
        )
        .add_functions("@function get-color($color) { @return $color; }")
        .add_rules(
            """
            strong { color: $primary; }
            .sidebar-title { color: $danger; }
            """,
            ".special { color: $warning; }",
        )
        .add_mixins("@mixin alert { color: $alert; }")
    )

    check_vars = [
        "_preset",
        "name",
        "_functions",
        "_defaults",
        "_mixins",
        "_rules",
        "_css",
    ]

    theme_dict = {k: v for k, v in vars(theme).items() if k in check_vars}

    assert theme_dict == {
        "_preset": "shiny",
        "name": None,
        "_functions": ["@function get-color($color) { @return $color; }"],
        "_defaults": [
            "$headings-color: red !default;",
            "$bar-color: purple !default;",
            "$select-color-text: green !default;",
            "$bslib-dashboard-design: true !default;",
        ],
        "_mixins": ["@mixin alert { color: $alert; }"],
        "_rules": [
            "\nstrong { color: $primary; }\n.sidebar-title { color: $danger; }\n",
            ".special { color: $warning; }",
        ],
        "_css": "",
    }


def test_theme_preset_must_be_valid():
    with pytest.raises(ValueError, match="Invalid preset"):
        Theme("not_a_valid_preset")  # type: ignore


@skip_on_windows
@pytest.mark.parametrize("preset", shiny_theme_presets)
def test_theme_css_compiles_and_is_cached(preset: ShinyThemePreset):
    theme = Theme(preset)

    assert theme._css == ""
    assert theme._can_use_precompiled() == (preset in shiny_theme_presets_bundled)

    # Adding rules resets the theme's cached CSS
    theme.add_rules(".MY_RULE { color: red; }")
    assert theme._css == ""

    first_css = theme.to_css()
    assert first_css.find("Bootstrap") != -1
    assert first_css.find(".MY_RULE") != -1
    assert theme.to_css() == first_css  # Cached value is returned

    # Adding another customization resets the theme's cached CSS
    theme.add_mixins(".MY_MIXIN { color: blue; }")
    second_css = theme.to_css()
    assert second_css != first_css, "First and second compiled CSS are the same"
    assert second_css.find("Bootstrap") != -1
    assert second_css.find(".MY_MIXIN") != -1


def _css_rule_body(css: str, selector: str) -> str:
    matches = re.findall(rf"{re.escape(selector)}\s*\{{([^}}]*)\}}", css)
    assert matches
    return re.sub(r"\s+", "", matches[-1])


def test_theme_update_preset():
    theme = Theme("shiny")
    assert theme._preset == "shiny"
    assert theme._can_use_precompiled() == ("shiny" in shiny_theme_presets_bundled)

    theme.preset = "bootstrap"
    assert theme._preset == "bootstrap"
    assert theme._can_use_precompiled() == ("bootstrap" in shiny_theme_presets_bundled)

    theme.preset = "sketchy"
    assert theme._preset == "sketchy"
    assert theme._can_use_precompiled() == ("sketchy" in shiny_theme_presets_bundled)

    with pytest.raises(ValueError, match="Invalid preset"):
        theme.preset = "not_a_valid_preset"  # type: ignore


def test_theme_defaults_positional_or_keyword():
    with pytest.raises(ValueError, match="Cannot provide both"):
        Theme("shiny").add_defaults("$color: red;", other_color="green")


def test_theme_keywords():
    theme = Theme("shiny")
    with pytest.raises(TypeError, match="my_function"):
        # Named kwargs aren't allowed in `.add_functions()` (anti-pattern)
        theme.add_functions(my_function="function")  # type: ignore

    theme.add_defaults(my_default1=True)
    theme.add_defaults(my_default2=False)
    theme.add_mixins(my_mixin=1)
    theme.add_rules(my_rule=3.141596, my_other_rule=None)

    assert theme._functions == []
    assert theme._defaults == [
        "$my-default2: false !default;",
        "$my-default1: true !default;",
    ]
    assert theme._mixins == ["$my-mixin: 1;"]
    assert theme._rules == [
        "$my-rule: 3.141596;",
        "$my-other-rule: null;",
    ]


def test_theme_is_not_tagifiable():
    with pytest.raises(SyntaxError, match="not meant to be used"):
        Theme("shiny").tagify()


def _page_sidebar(*args, **kwargs) -> Tag:  # type: ignore
    return page_sidebar(sidebar("Sidebar"), *args, **kwargs)  # type: ignore


@skip_on_windows
@pytest.mark.parametrize(
    "page_fn",
    [
        page_bootstrap,
        page_fillable,
        _page_sidebar,  # type: ignore
    ],
)
@pytest.mark.parametrize(
    "theme",
    [None, Theme("shiny"), Theme("bootstrap"), Theme("sketchy")],
)
def test_page_theme_wins(page_fn: Callable[..., Tag], theme: Optional[Theme]):
    ui = page_fn(
        input_dark_mode(),
        input_date_range("date", "Date Range"),
        input_selectize("select", "Select", choices=["A", "B"]),
        input_slider("slider", "Slider", min=0, max=100, value=50),
        theme=theme,
    )

    app = App(ui, lambda inputs: None)._render_page(ui, "lib")

    deps = app["dependencies"]
    no_css = [
        "shiny",
        "bslib-components",
        "ionrangeslider",
        "bootstrap-datepicker",
        "selectize",
    ]

    for dep in deps:
        if dep.name in no_css:
            # These components should have CSS suppressed by the page-level
            # dependency from shiny_page_theme_deps(). If this test fails, it means
            # that our assumptions about how htmltools' dependency resolution works
            # have changed.
            assert dep.stylesheet == []


def test_theme_dep_name_is_valid_path_part():
    theme = Theme("shiny")
    assert theme._dep_create("foo.css").name == "shiny-theme-shiny"

    theme = Theme("bootstrap", name="default")
    assert theme._dep_create("foo.css").name == "shiny-theme-default"

    theme = Theme("sketchy", name="My Special Sketchy")
    assert theme._dep_create("foo.css").name == "shiny-theme-my-special-sketchy"


def test_theme_dependency_has_data_attribute():
    theme = Theme("shiny")
    assert theme._html_dependencies()[0].stylesheet[0]["data-shiny-theme"] == "shiny"  # type: ignore

    theme = Theme("shiny", name="My Fancy Theme")
    assert theme._html_dependencies()[0].stylesheet[0]["data-shiny-theme"] == "My Fancy Theme"  # type: ignore


def test_theme_add_sass_layer_file():
    with tempfile.TemporaryDirectory() as temp_dir:
        with open(f"{temp_dir}/no-layers.scss", "w") as f:
            f.write("// no layers")

        # Throws if no special layer boundary comments are found
        with pytest.raises(ValueError, match="one layer boundary"):
            Theme().add_sass_layer_file(f"{temp_dir}/no-layers.scss")

        with open(f"{temp_dir}/layers.scss", "w") as temp_scss:
            temp_scss.write("""
/*-- scss:uses --*/
// uses
/*-- scss:functions --*/
// functions
/*-- scss:defaults --*/
// defaults 1
/*-- scss:mixins --*/
// mixins
/*-- scss:rules --*/
// rules 1
/*-- scss:defaults --*/
// defaults 2
/*-- scss:rules --*/
// rules 2
            """)

        theme = Theme().add_sass_layer_file(temp_scss.name)

    assert theme._uses == ["// uses\n"]
    assert theme._functions == ["// functions\n"]
    assert theme._defaults == ["// defaults 1\n// defaults 2\n"]
    assert theme._mixins == ["// mixins\n"]
    assert theme._rules == ["// rules 1\n// rules 2\n"]


@skip_on_windows
@pytest.mark.parametrize("preset", shiny_theme_presets)
def test_theme_from_brand_base_case_compiles(preset: str):
    brand_txt = f"""
meta:
  name: Brand Test
defaults:
  shiny:
    theme:
      preset: {preset}
    """

    with tempfile.TemporaryDirectory() as tmpdir:
        with open(f"{tmpdir}/_brand.yml", "w") as f:
            f.write(brand_txt)

        theme = Theme.from_brand(f"{tmpdir}")

        # Check that the theme preset is set from the brand
        assert theme.preset == preset

        # Check that the brand Sass layer is included
        assert any(["brand-choose" in f for f in theme._functions])
        assert any(["brand: initial" in d for d in theme._defaults])
        assert any(["brand: brand rules" in r for r in theme._rules])

        # Check that the CSS compiles without error
        css = theme.to_css({"output_style": "expanded"})
        assert isinstance(css, str)


@skip_on_windows
def test_theme_from_brand_light_dark_colors_emit_complete_mode_layers():
    brand_txt = """
color:
  foreground:
    light: "#111111"
    dark: "#eeeeee"
  background:
    light: "#ffffff"
    dark: "#222222"
  primary:
    light: "#0066cc"
    dark: "#66b2ff"
  link:
    light: "#0055aa"
    dark: "#99ccff"
typography:
  headings:
    color: foreground
  monospace-inline:
    color: foreground
    background-color:
      light: "#f1f5fa"
      dark: "#263746"
  monospace-block:
    color: foreground
    background-color:
      light: "#f8f9fa"
      dark: "#1f2933"
  link:
    color: link
    background-color:
      light: "#eef6ff"
      dark: "#203040"
"""

    with tempfile.TemporaryDirectory() as tmpdir:
        with open(f"{tmpdir}/_brand.yml", "w") as f:
            f.write(brand_txt)

        theme = Theme.from_brand(tmpdir)
        css = theme.to_css({"output_style": "expanded"})

    assert '[data-bs-theme="light"]' in css
    assert '[data-bs-theme="dark"]' in css
    assert "--brand-color-foreground: #111111" in css
    assert "--brand-color-foreground: #eeeeee" in css

    light_root = _css_rule_body(css, "html:not([data-bs-theme])")
    explicit_light_root = _css_rule_body(css, '[data-bs-theme="light"]')
    dark_root = _css_rule_body(css, '[data-bs-theme="dark"]')

    for root, expected in (
        (light_root, ("#111111", "17,17,17", "#ffffff", "255,255,255")),
        (
            explicit_light_root,
            ("#111111", "17,17,17", "#ffffff", "255,255,255"),
        ),
        (dark_root, ("#eeeeee", "238,238,238", "#222222", "34,34,34")),
    ):
        foreground, foreground_rgb, background, background_rgb = expected
        assert f"--bs-body-color:{foreground}" in root
        assert f"--bs-body-color-rgb:{foreground_rgb}" in root
        assert f"--bs-body-bg:{background}" in root
        assert f"--bs-body-bg-rgb:{background_rgb}" in root

    assert "--bs-primary:#0066cc" in light_root
    assert "--bs-primary-rgb:0,102,204" in light_root
    assert "--bs-link-color:#0055aa" in light_root
    assert "--bs-link-color-rgb:0,85,170" in light_root
    assert "--bs-heading-color:#111111" in light_root
    assert "--bs-code-color:#111111" in light_root
    assert "--bs-code-bg:#f1f5fa" in light_root
    assert "--bs-pre-color:#111111" in light_root
    assert "--bs-pre-bg:#f8f9fa" in light_root
    assert "--bs-link-bg:#eef6ff" in light_root

    assert "--bs-primary:#66b2ff" in dark_root
    assert "--bs-primary-rgb:102,178,255" in dark_root
    assert "--bs-link-color:#99ccff" in dark_root
    assert "--bs-link-color-rgb:153,204,255" in dark_root
    assert "--bs-heading-color:#eeeeee" in dark_root

    light_button = _css_rule_body(css, "html:not([data-bs-theme]) .btn-primary")
    dark_button = _css_rule_body(css, '[data-bs-theme="dark"] .btn-primary')
    assert "--bs-btn-bg:#0066cc" in light_button
    assert "--bs-btn-border-color:#0066cc" in light_button
    assert "--bs-btn-bg:#66b2ff" in dark_button
    assert "--bs-btn-border-color:#66b2ff" in dark_button

    assert "color:var(--bs-code-color)" in _css_rule_body(
        css, "html:not([data-bs-theme]) code:not(pre > code)"
    )
    assert "background-color:var(--bs-code-bg)" in _css_rule_body(
        css, '[data-bs-theme="dark"] code:not(pre > code)'
    )
    assert "color:var(--bs-pre-color)" in _css_rule_body(
        css, "html:not([data-bs-theme]) pre"
    )
    assert "background-color:var(--bs-pre-bg)" in _css_rule_body(
        css, '[data-bs-theme="dark"] pre'
    )


@skip_on_windows
def test_theme_from_brand_partial_color_omits_missing_mode_mapping():
    brand_txt = """
color:
  background:
    dark: "#222222"
  primary:
    light: "#0066cc"
  link:
    light: "#0055aa"
typography:
  headings:
    color: background
  monospace-inline:
    background-color:
      dark: "#303030"
  monospace-block:
    color:
      light: "#202020"
    background-color:
      dark: "#181818"
"""

    with tempfile.TemporaryDirectory() as tmpdir:
        with open(f"{tmpdir}/_brand.yml", "w") as f:
            f.write(brand_txt)

        theme = Theme.from_brand(tmpdir)
        css = theme.to_css({"output_style": "expanded"})

    assert "--brand-color-background: #222222" in css
    assert css.count("--brand-color-background: #222222") == 1
    assert "--brand-color-primary: #0066cc" in css

    light_root = _css_rule_body(css, "html:not([data-bs-theme])")
    explicit_light_root = _css_rule_body(css, '[data-bs-theme="light"]')
    dark_root = _css_rule_body(css, '[data-bs-theme="dark"]')

    assert "--bs-primary:#0066cc" in light_root
    assert "--bs-primary-rgb:0,102,204" in light_root
    assert "--bs-primary:#0066cc" in explicit_light_root
    assert "--bs-link-color:#0055aa" in light_root
    assert "--bs-link-color-rgb:0,85,170" in light_root
    assert "--bs-body-bg:" not in light_root
    assert "--bs-heading-color:" not in light_root

    assert "--bs-primary:" not in dark_root
    assert "--bs-primary-rgb:" not in dark_root
    assert "--bs-link-color:" not in dark_root
    assert "--bs-link-color-rgb:" not in dark_root
    assert "--bs-body-bg:#222222" in dark_root
    assert "--bs-body-bg-rgb:34,34,34" in dark_root
    assert "--bs-heading-color:#222222" in dark_root
    assert "--bs-code-bg:#303030" in dark_root
    assert "--bs-pre-bg:#181818" in dark_root
    assert "--bs-pre-color:" not in dark_root

    assert "--bs-btn-bg:#0066cc" in _css_rule_body(
        css, "html:not([data-bs-theme]) .btn-primary"
    )
    assert '[data-bs-theme="dark"] .btn-primary{' not in css
    assert "html:not([data-bs-theme]) code:not(pre > code) {" not in css
    assert (
        _css_rule_body(css, '[data-bs-theme="dark"] code:not(pre > code)')
        == "background-color:var(--bs-code-bg);"
    )
    assert (
        _css_rule_body(css, "html:not([data-bs-theme]) pre")
        == "color:var(--bs-pre-color);"
    )
    assert (
        _css_rule_body(css, '[data-bs-theme="dark"] pre')
        == "background-color:var(--bs-pre-bg);"
    )


@skip_on_windows
def test_theme_from_brand_scalar_values_are_emitted_in_both_modes():
    brand_txt = """
color:
  primary: "#0066cc"
typography:
  headings:
    color: "#333333"
  monospace-inline:
    color: "#111111"
    background-color: "#f1f5fa"
  monospace-block:
    color: "#222222"
    background-color: "#f8f9fa"
"""

    with tempfile.TemporaryDirectory() as tmpdir:
        with open(f"{tmpdir}/_brand.yml", "w") as f:
            f.write(brand_txt)

        theme = Theme.from_brand(tmpdir)
        css = theme.to_css({"output_style": "expanded"})

    assert css.count("--brand-color-primary: #0066cc") == 2
    assert css.count("--brand-typography-headings-color: #333333") == 2
    assert css.count("--brand-typography-monospace-inline-color: #111111") == 2
    assert (
        css.count("--brand-typography-monospace-inline-background-color: #f1f5fa") == 2
    )
    assert css.count("--brand-typography-monospace-block-color: #222222") == 2
    assert (
        css.count("--brand-typography-monospace-block-background-color: #f8f9fa") == 2
    )
    light_root = _css_rule_body(css, "html:not([data-bs-theme])")
    dark_root = _css_rule_body(css, '[data-bs-theme="dark"]')
    for root in (light_root, dark_root):
        assert "--bs-primary:#0066cc" in root
        assert "--bs-primary-rgb:0,102,204" in root
        assert "--bs-heading-color:#333333" in root
        assert "--bs-code-color:#111111" in root
        assert "--bs-code-bg:#f1f5fa" in root
        assert "--bs-pre-color:#222222" in root
        assert "--bs-pre-bg:#f8f9fa" in root

    assert "--bs-btn-bg:#0066cc" in _css_rule_body(
        css, "html:not([data-bs-theme]) .btn-primary"
    )
    assert "--bs-btn-bg:#0066cc" in _css_rule_body(
        css, '[data-bs-theme="dark"] .btn-primary'
    )


@skip_on_windows
def test_theme_from_brand_retains_variant_values_for_runtime_switching():
    brand_txt = """
color:
  primary:
    light: "#0066cc"
    dark: "#66b2ff"
"""

    with tempfile.TemporaryDirectory() as tmpdir:
        with open(f"{tmpdir}/_brand.yml", "w") as f:
            f.write(brand_txt)

        theme = Theme.from_brand(tmpdir)

    assert theme.brand.color is not None
    primary = theme.brand.color.primary
    assert primary is not None
    assert not isinstance(primary, str)
    assert primary.light == "#0066cc"
    assert primary.dark == "#66b2ff"
    assert all("brand_color_primary: {" not in default for default in theme._defaults)


@skip_on_windows
def test_theme_from_brand_primary_supplies_default_link_color():
    brand_txt = """
color:
  primary:
    light: "#cc0000"
    dark: "#00aa44"
"""

    with tempfile.TemporaryDirectory() as tmpdir:
        with open(f"{tmpdir}/_brand.yml", "w") as f:
            f.write(brand_txt)

        css = Theme.from_brand(tmpdir).to_css({"output_style": "expanded"})

    assert "--bs-link-color:#cc0000" in _css_rule_body(css, "html:not([data-bs-theme])")
    assert "--bs-link-color-rgb:204,0,0" in _css_rule_body(
        css, "html:not([data-bs-theme])"
    )
    assert "--bs-link-color:#00aa44" in _css_rule_body(css, '[data-bs-theme="dark"]')
    assert "--bs-link-color-rgb:0,170,68" in _css_rule_body(
        css, '[data-bs-theme="dark"]'
    )


@skip_on_windows
def test_theme_from_brand_respects_custom_bootstrap_prefix():
    brand_txt = """
color:
  foreground:
    light: "#111111"
    dark: "#eeeeee"
  primary:
    light: "#cc0000"
    dark: "#00aa44"
defaults:
  bootstrap:
    defaults:
      prefix: acme-
"""

    with tempfile.TemporaryDirectory() as tmpdir:
        with open(f"{tmpdir}/_brand.yml", "w") as f:
            f.write(brand_txt)

        css = Theme.from_brand(tmpdir).to_css({"output_style": "expanded"})

    light_root = _css_rule_body(css, "html:not([data-bs-theme])")
    dark_root = _css_rule_body(css, '[data-bs-theme="dark"]')
    light_button = _css_rule_body(css, "html:not([data-bs-theme]) .btn-primary")
    dark_button = _css_rule_body(css, '[data-bs-theme="dark"] .btn-primary')

    assert "--acme-body-color:#111111" in light_root
    assert "--acme-body-color-rgb:17,17,17" in light_root
    assert "--acme-primary:#cc0000" in light_root
    assert "--acme-primary-rgb:204,0,0" in light_root
    assert "--acme-btn-bg:#cc0000" in light_button
    assert "--acme-body-color:#eeeeee" in dark_root
    assert "--acme-primary:#00aa44" in dark_root
    assert "--acme-btn-bg:#00aa44" in dark_button
    assert "--bs-primary:var(--brand-color-primary)" not in css
