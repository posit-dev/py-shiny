import pytest

from shiny.ui import Theme
from shiny.ui._theme import (
    ShinyThemePreset,
    ShinyThemePresets,
    ShinyThemePresetsBundled,
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
            "$headings_color: red;",
            "$bar_color: purple;",
            "$select_color_text: green;",
            "$bslib_dashboard_design: true;",
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


@pytest.mark.parametrize("preset", ShinyThemePresets)
def test_theme_css_compiles_and_is_cached(preset: ShinyThemePreset):
    theme = Theme(preset)
    if preset in ShinyThemePresetsBundled:
        assert theme._css == "precompiled"
    else:
        assert theme._css == ""

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
    assert theme._css == "precompiled" if "shiny" in ShinyThemePresetsBundled else ""

    theme.preset = "bootstrap"
    assert theme._preset == "bootstrap"
    assert theme._css == (
        "precompiled" if "bootstrap" in ShinyThemePresetsBundled else ""
    )

    theme.preset = "sketchy"
    assert theme._preset == "sketchy"
    assert theme._css == (
        "precompiled" if "sketchy" in ShinyThemePresetsBundled else ""
    )

    with pytest.raises(ValueError, match="Invalid preset"):
        theme.preset = "not_a_valid_preset"  # type: ignore


def test_theme_defaults_positional_or_keyword():
    with pytest.raises(ValueError, match="Cannot provide both"):
        Theme("shiny").add_defaults("$color: red;", other_color="green")
