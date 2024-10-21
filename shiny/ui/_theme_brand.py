from __future__ import annotations

from pathlib import Path
from typing import Any

from brand_yml import Brand, read_brand_yml

from ._theme import Theme

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

color_extras_map = {
    "foreground": ["body-color", "pre-color"],
    "background": ["body-bg"],
    "secondary": ["body-secondary-color", "body-secondary"],
    "tertiary": ["body-tertiary-color", "body-tertiary"],
}


class BrandTheme(Brand):
    def __init__(self, brand_yml: str | Path | None = None, *args: Any, **kwargs: Any):
        if brand_yml is not None and len(args) == 0:
            if len(kwargs) > 0:
                raise ValueError("Cannot pass both `brand_yml` and `**kwargs`")
            data: dict[str, Any] = read_brand_yml(brand_yml, as_data=True)
            super().__init__(**data)
            return
        if brand_yml is not None and len(args) > 0:
            args = (brand_yml, *args)

        super().__init__(*args, **kwargs)

    @classmethod
    def from_brand(cls, brand: Brand):
        return cls.model_validate(brand.model_dump())

    def theme(self) -> Theme:
        colors: dict[str, str] = {}
        if self.color:
            colors: dict[str, str] = {
                k: v
                for k, v in self.color.model_dump(exclude_none=True).items()
                if k != "palette"
            }

            for extra, sass_var_list in color_extras_map.items():
                if extra in colors:
                    sass_vars = {var: colors[extra] for var in sass_var_list}
                    colors = {**colors, **sass_vars}

        typography: dict[str, str] = {}
        if self.typography:
            for field in self.typography.model_fields.keys():
                if field == "fonts":
                    continue
                type_prop = getattr(self.typography, field)
                if type_prop is None:
                    continue
                for k, v in type_prop.model_dump(exclude_none=True).items():
                    if k in typography_map[field]:
                        typography[typography_map[field][k]] = v
                    else:
                        print(f"skipping {field}.{k} not mapped")

        brand_colors_sass_vars: dict[str, str] = {}
        brand_colors_css_vars: list[str] = []

        if self.color and self.color.palette is not None:
            brand_colors_sass_vars.update(
                {f"brand-{k}": v for k, v in self.color.palette.items()}
            )

            for k, v in self.color.palette.items():
                brand_colors_css_vars.append(f"--brand-{k}: {v};")

        sass_vars: dict[str, str] = {**brand_colors_sass_vars, **colors, **typography}
        sass_vars = {k: v for k, v in sass_vars.items()}

        name: str = "brand"
        if self.meta and self.meta.name:
            name = self.meta.name.full or self.meta.name.short or "brand"

        return (
            Theme(name=name)
            .add_defaults(
                **{
                    "code-font-weight": "normal",
                    "link-bg": None,
                    "link-weight": None,
                }
            )
            .add_defaults(**sass_vars)
            .add_defaults(
                self.typography.css_include_fonts() if self.typography else ""
            )
            .add_rules(":root {", *brand_colors_css_vars, "}")
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
            """
            )
            .add_rules("code { font-weight: $code-font-weight; }")
        )
