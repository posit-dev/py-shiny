from __future__ import annotations

import warnings
from pathlib import Path
from typing import Any, Optional

from brand_yml import Brand
from htmltools import HTMLDependency

from .._versions import bootstrap
from ._theme import Theme
from ._theme_presets import ShinyThemePreset, shiny_theme_presets

color_extras_map = {
    "foreground": ["body-color", "pre-color"],
    "background": ["body-bg"],
    "secondary": ["body-secondary-color", "body-secondary"],
    "tertiary": ["body-tertiary-color", "body-tertiary"],
}
"""Maps brand.color fields to Bootstrap Sass variables"""

bootstrap_colors = {
    "5": [
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
        "black",
        "white",
        "gray",
        "gray-dark",
    ]
}
"""
Colors known to Bootstrap

* [Bootstrap 5 - Colors](https://getbootstrap.com/docs/5.3/customize/color/#color-sass-maps)
"""

typography_map = {
    "base": {
        "family": "font-family-base",
        "size": "font-size-base",
        "line_height": "line-height-base",
        "weight": "font-weight-base",
    },
    "headings": {
        "family": "headings-font-family",
        "line_height": "headings-line-height",
        "weight": "headings-font-weight",
        "color": "headings-color",
        "style": "headings-style",
    },
    "monospace": {
        "family": "font-family-monospace",
        "size": "code-font-size",
    },
    "monospace_inline": {
        "family": "font-family-monospace-inline",
        "color": "code-color",
        "background_color": "code-bg",
        "size": "code-inline-font-size",
        "weight": "code-font-weight",
    },
    "monospace_block": {
        "family": "font-family-monospace-block",
        "line_height": "pre-line-height",
        "color": "pre-color",
        "background_color": "pre-bg",
    },
    "link": {
        "background_color": "link-bg",
        "color": "link-color",
        "weight": "link-weight",
        "decoration": "link-decoration",
    },
}
"""Maps brand.typography fields to corresponding Bootstrap Sass variables"""


class BrandBootstrap:
    """Convenience class for storing Bootstrap defaults from a brand instance"""

    def __init__(
        self,
        version: Any = bootstrap,
        preset: Any = "shiny",
        **kwargs: str | int | bool | float | None,
    ):
        if not isinstance(version, (str, int)):
            raise ValueError(
                f"Bootstrap version must be a string or integer, not {version!r}."
            )

        if version != bootstrap:
            warnings.warn(
                f"Shiny does not current support Bootstrap version {version}. "
                f"Using Bootstrap v{bootstrap} instead.",
                stacklevel=4,
            )
            version = bootstrap

        if not isinstance(preset, str) or preset not in shiny_theme_presets:
            raise ValueError(
                f"{preset!r} is not a valid Bootstrap preset provided by Shiny. "
                f"Valid presets are {shiny_theme_presets}."
            )

        self.version: str = str(version)
        self.preset: ShinyThemePreset = preset
        self.defaults = kwargs

    @classmethod
    def from_brand(cls, brand: Brand):
        defaults: dict[str, str | int | bool | float | None] = {}

        if brand.defaults:
            if brand.defaults and "bootstrap" in brand.defaults:
                defaults.update(brand.defaults["bootstrap"])
            if "shiny" in brand.defaults and "theme" in brand.defaults["shiny"]:
                defaults.update(brand.defaults["shiny"]["theme"])

        return cls(**defaults)


class ThemeBrand(Theme):
    def __init__(
        self,
        brand: Brand,
        preset: ShinyThemePreset = "shiny",
        name: Optional[str] = None,
        include_paths: Optional[str | Path | list[str | Path]] = None,
    ):
        super().__init__(preset=preset, name=name, include_paths=include_paths)
        self.brand = brand

    def _html_dependencies(self) -> list[HTMLDependency]:
        theme_deps = super()._html_dependencies()

        if not self.brand.typography:
            return theme_deps

        # We're going to put the fonts dependency _inside_ the theme's tempdir, which
        # relies on the theme's dependency having `all_files=True`.
        temp_dir = self._get_css_tempdir()
        temp_path = Path(temp_dir) / "fonts"
        temp_path.mkdir(parents=True, exist_ok=True)

        fonts_dep = self.brand.typography.fonts_html_dependency(
            path_dir=temp_path,
            name=f"{self._dep_name()}-fonts",
            version=self._version,
        )

        if fonts_dep is None:
            return theme_deps

        return [fonts_dep, *theme_deps]




def theme_from_brand(brand: str | Path | Brand) -> Theme:
    """
    Create a custom Shiny theme from a `_brand.yml`

    Creates a custom Shiny theme for your brand using
    [brand.yml](https://posit-dev.github.io/brand-yml), which may be either an instance
    of :class:`brand_yml.Brand` or a :class:`Path` used by
    :meth:`brand_yml.Brand.from_yaml` to locate the `_brand.yml` file.

    Parameters
    ----------
    brand
        A :class:`brand_yml.Brand` instance, or a path to help locate `_brand.yml`.
        For a path, you can pass `__file__` or a directory containing the `_brand.yml`
        or a path directly to the `_brand.yml` file.

    Returns
    -------
    :
        A :class:`shiny.ui.Theme` instance with a custom Shiny theme created from the
        brand guidelines (see :class:`brand_yml.Brand`).
    """
    if not isinstance(brand, Brand):
        brand = Brand.from_yaml(brand)

    if not isinstance(brand, Brand):
        raise ValueError("Invalid `brand`, must be a path or a Brand instance.")

    brand_bootstrap = BrandBootstrap.from_brand(brand)

    colors: dict[str, str] = {}
    if brand.color:
        colors: dict[str, str] = {
            k: v
            for k, v in brand.color.model_dump(exclude_none=True).items()
            if k != "palette"
        }

        for extra, sass_var_list in color_extras_map.items():
            if extra in colors:
                brand_sass_vars = {var: colors[extra] for var in sass_var_list}
                colors = {**colors, **brand_sass_vars}

    typography: dict[str, str] = {}
    if brand.typography:
        for field in brand.typography.model_fields.keys():
            if field == "fonts":
                continue
            type_prop = getattr(brand.typography, field)
            if type_prop is None:
                continue
            for k, v in type_prop.model_dump(exclude_none=True).items():
                if k in typography_map[field]:
                    typography[typography_map[field][k]] = v
                else:
                    # TODO: Need to catch these and map to appropriate Bootstrap vars
                    print(f"skipping {field}.{k} not mapped")

    brand_colors_sass_vars: dict[str, str] = {}
    brand_colors_css_vars: list[str] = []

    if brand.color and brand.color.palette is not None:
        brand_colors_sass_vars.update(
            {f"brand-{k}": v for k, v in brand.color.palette.items()}
        )

        for k, v in brand.color.palette.items():
            brand_colors_css_vars.append(f"--brand-{k}: {v};")

    brand_sass_vars: dict[str, str] = {**brand_colors_sass_vars, **colors, **typography}
    brand_sass_vars = {k: v for k, v in brand_sass_vars.items()}

    name: str = "brand"
    if brand.meta and brand.meta.name:
        name = brand.meta.name.full or brand.meta.name.short or "brand"

    return (
        ThemeBrand(
            brand,
            name=name,
            preset=brand_bootstrap.preset,
        )
        # Defaults are added in reverse order, so each chunk appears above the next
        # layer of defaults. The intended order in the final output is:
        # 1. Brand Sass vars (colors, typography)
        # 2. Brand Bootstrap Sass vars
        # 3. Fallback vars needed by additional Brand rules
        .add_defaults(
            # Variables we create to augment Bootstrap's variables
            **{
                "code-font-weight": "normal",
                "link-bg": None,
                "link-weight": None,
            }
        )
        .add_defaults(**brand_bootstrap.defaults)
        .add_defaults(**brand_sass_vars)
        .add_defaults(brand.typography.css_include_fonts() if brand.typography else "")
        # Brand Rules ----
        .add_rules(":root {", *brand_colors_css_vars, "}")
        # Additional rules to fill in Bootstrap styles for Brand parameters
        .add_rules(
            """
            // https://github.com/twbs/bootstrap/blob/5c2f2e7e0ec41daae3819106efce20e2568b19d2/scss/_root.scss#L82
            :root {
                --#{$prefix}link-bg: #{$link-bg};
                --#{$prefix}link-weight: #{$link-weight};
            }
            // https://github.com/twbs/bootstrap/blob/5c2f2e7e0ec41daae3819106efce20e2568b19d2/scss/_reboot.scss#L244
            a {
                background-color: var(--#{$prefix}link-bg);
                font-weight: var(--#{$prefix}link-weight);
            }
            code {
                font-weight: $code-font-weight;
            }
            """
        )
    )
