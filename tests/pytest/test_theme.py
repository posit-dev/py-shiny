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
            temp_scss.write(
                """
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
            """
            )

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
        css = theme.to_css()
        assert isinstance(css, str)
