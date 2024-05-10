import pytest

from shiny.ui import Theme
from shiny.ui._theme import (
    ShinyThemePreset,
    shiny_theme_presets,
    shiny_theme_presets_bundled,
)


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
            "$headings-color: red;",
            "$bar-color: purple;",
            "$select-color-text: green;",
            "$bslib-dashboard-design: true;",
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
    theme.add_functions(my_function="function")
    theme.add_defaults(my_default1=True)
    theme.add_defaults(my_default2=False)
    theme.add_mixins(my_mixin=1)
    theme.add_rules(my_rule=3.141596, my_other_rule=None)

    assert theme._functions == ["$my-function: function;"]
    assert theme._defaults == [
        "$my-default2: false;",
        "$my-default1: true;",
    ]
    assert theme._mixins == ["$my-mixin: 1;"]
    assert theme._rules == [
        "$my-rule: 3.141596;",
        "$my-other-rule: null;",
    ]
