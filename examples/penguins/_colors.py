import matplotlib.colors as mpl_colors
import seaborn as sns  # type: ignore

# "darkorange", "purple", "cyan4"
_colors = [[255, 140, 0], [160, 32, 240], [0, 139, 139]]
_colors = [(r / 255.0, g / 255.0, b / 255.0) for r, g, b in _colors]

palette: dict[str, tuple[float, float, float]] = {
    "Adelie": _colors[0],
    "Chinstrap": _colors[1],
    "Gentoo": _colors[2],
    "default": sns.color_palette()[0],  # type: ignore
}


bg_palette = {}
# bgcols: list[str] = sns.color_palette().as_hex()
# Use `sns.set_style("whitegrid")` to help find approx alpha value
for name, col in palette.items():
    bg_palette[name] = mpl_colors.to_hex(mpl_colors.to_rgba(col, 0.25), keep_alpha=True)  # type: ignore


# default_color: str = sns.color_palette().as_hex()[0]  # type: ignore
