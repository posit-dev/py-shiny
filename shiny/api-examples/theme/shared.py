from pathlib import Path

from shiny import ui

my_theme = (
    ui.Theme("shiny", include_paths=Path(__file__).parent)
    .add_defaults(
        bslib_dashboard_design=True,
    )
    .add_mixins(
        headings_color="$success",
        bar_color="$purple",
        select_color_text="$orange",
    )
    .add_rules(
        """
        em { color: $warning; }
        .sidebar-title { color: $danger; }
        """
    )
    .add_rules('@import "css/rules.scss";')
)


if False:
    # To avoid runtime Sass compilation, save your theme CSS to a file
    # and then use that CSS file in the `theme` argument.
    css_dir = Path(__file__).parent / "css"
    css_dir.mkdir(exist_ok=True)
    with open(css_dir / "shiny-theme-demo.css", "w") as f:
        f.write(my_theme.to_css())

filler_text = """
**AI-generated filler text.** In the world of exotic fruits, the durian stands out with its spiky exterior and strong odor. Despite its divisive smell, many people are drawn to its rich, creamy texture and unique flavor profile. This tropical fruit is often referred to as the "king of fruits" in various Southeast Asian countries.

Durians are known for their large size and thorn-covered husk, _which requires careful handling_. The flesh inside can vary in color from pale yellow to deep orange, with a custard-like consistency that melts in your mouth. Some describe its taste as a mix of sweet, savory, and creamy, while others find it overpowering and pungent.
"""
