from __future__ import annotations

import warnings
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional, Union

if TYPE_CHECKING:
    from brand_yml import Brand
from htmltools import HTMLDependency

from .._versions import bootstrap as v_bootstrap
from ._theme import Theme
from ._utils import path_pkg_www

YamlScalarType = Union[str, int, bool, float, None]

# https://github.com/twbs/bootstrap/blob/6e1f75/scss/_variables.scss#L38-L49
bootstrap_colors: list[str] = [
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
"""
Colors known to Bootstrap

When these colors are named in `colors.palette`, we'll map the brand's colors to the
corresponding Bootstrap color Sass variable.

* [Bootstrap 5 - Colors](https://getbootstrap.com/docs/5.3/customize/color/#color-sass-maps)
"""


class BrandBootstrapConfigFromYaml:
    """Validate a Bootstrap config from a YAML source"""

    def __init__(
        self,
        path: str,
        version: Any = None,
        preset: Any = None,
        functions: Any = None,
        defaults: Any = None,
        mixins: Any = None,
        rules: Any = None,
    ):
        # TODO: Remove `path` and handle in try/except block in caller
        self._path = path
        self.version = version
        self.preset: str | None = self._validate_str(preset, "preset")
        self.functions: str | None = self._validate_str(functions, "functions")
        self.defaults: dict[str, YamlScalarType] | None = self._validate_defaults(
            defaults
        )
        self.mixins: str | None = self._validate_str(mixins, "mixins")
        self.rules: str | None = self._validate_str(rules, "rules")

    def _validate_str(self, x: Any, param: str) -> str | None:
        if x is None or isinstance(x, str):
            return x

        raise ValueError(
            f"Invalid brand `{self._path}.{param}`. Must be a string or empty."
        )

    def _validate_defaults(self, x: Any) -> dict[str, YamlScalarType] | None:
        if x is None:
            return None

        if not isinstance(x, dict):
            raise ValueError(
                f"Invalid brand `{self._path}.defaults`, must be a dictionary."
            )

        y: dict[Any, Any] = x

        if not all([isinstance(k, str) for k in y.keys()]):
            raise ValueError(
                f"Invalid brand `{self._path}.defaults`, all keys must be strings."
            )

        if not all(
            [v is None or isinstance(v, (str, int, float, bool)) for v in y.values()]
        ):
            raise ValueError(
                f"Invalid brand `{self._path}.defaults`, all values must be scalar."
            )

        res: dict[str, YamlScalarType] = y
        return res


class BrandBootstrapConfig:
    """Convenience class for storing Bootstrap defaults from a brand instance"""

    def __init__(
        self,
        version: Any = v_bootstrap,
        preset: str | None = None,
        functions: str | None = None,
        defaults: dict[str, YamlScalarType] | None = None,
        mixins: str | None = None,
        rules: str | None = None,
    ):
        if not isinstance(version, (str, int)):
            raise ValueError(
                f"Bootstrap version must be a string or integer, not {version!r}."
            )

        v_major = str(version).split(".")[0]
        bs_major = str(v_bootstrap).split(".")[0]

        if v_major != bs_major:
            # TODO (bootstrap-update): Assumes Shiny ships one version of Bootstrap
            warnings.warn(
                f"Shiny does not current support Bootstrap version {v_major}. "
                f"Using Bootstrap v{bs_major} instead.",
                stacklevel=4,
            )
            v_major = bs_major

        self.version = v_major
        self.preset = preset
        self.functions = functions
        self.defaults = defaults
        self.mixins = mixins
        self.rules = rules

    @classmethod
    def from_brand(cls, brand: "Brand"):
        if not brand.defaults:
            return cls()

        shiny_args = {}
        if "shiny" in brand.defaults and "theme" in brand.defaults["shiny"]:
            shiny_args = brand.defaults["shiny"]["theme"]

        shiny = BrandBootstrapConfigFromYaml(
            path="defaults.shiny.theme",
            **shiny_args,
        )

        bs_args = {}
        if "bootstrap" in brand.defaults:
            bs_args = brand.defaults["bootstrap"]

        bootstrap = BrandBootstrapConfigFromYaml(
            path="defaults.bootstrap",
            **bs_args,
        )

        # now combine bootstrap and shiny config options in a way that makes sense
        def join_str(x: str | None, y: str | None):
            return "\n".join([z for z in [x, y] if z is not None])

        defaults: dict[str, YamlScalarType] = {}
        defaults.update(bootstrap.defaults or {})
        defaults.update(shiny.defaults or {})

        return cls(
            version=shiny.version or bootstrap.version or v_bootstrap,
            preset=shiny.preset or bootstrap.preset,
            functions=join_str(bootstrap.functions, shiny.functions),
            defaults=defaults,
            mixins=join_str(bootstrap.mixins, shiny.mixins),
            rules=join_str(bootstrap.rules, shiny.rules),
        )


class ThemeBrand(Theme):
    def __init__(
        self,
        brand: "Brand",
        *,
        include_paths: Optional[str | Path | list[str | Path]] = None,
    ):
        name = self._get_theme_name(brand)
        brand_bootstrap = BrandBootstrapConfig.from_brand(brand)

        # Initialize theme ------------------------------------------------------------
        super().__init__(
            name=name,
            preset=brand_bootstrap.preset,
            include_paths=include_paths,
        )

        self.brand = brand
        self.add_sass_layer_file(
            path_pkg_www("..", "py-shiny", "brand", "_brand-yml.scss")
        )

        # Prep Sass and CSS Variables -------------------------------------------------
        (
            brand_color_palette_defaults,
            brand_color_defaults,
            brand_color_palette_rules,
        ) = ThemeBrand._prepare_color_vars(brand)

        brand_typography_defaults = ThemeBrand._prepare_typography_vars(brand)

        # Defaults ----
        # Final order is reverse-insertion:
        # * brand.color.palette
        # * brand.defaults (Brand-defined Bootstrap defaults)
        # * brand.color
        # * brand.typography

        self._add_defaults_hdr("typography", **brand_typography_defaults)
        self._add_defaults_hdr("color", **brand_color_defaults)

        if brand_bootstrap.defaults:
            self._add_defaults_hdr("defaults (bootstrap)", **(brand_bootstrap.defaults))

        self._add_defaults_hdr("color.palette", **brand_color_palette_defaults)

        # Rules ----
        self.add_rules(*brand_color_palette_rules)

        # Bootstrap extras: functions, mixins, rules (defaults handled above)
        self._add_brand_bootstrap_other(brand_bootstrap)

    def _get_theme_name(self, brand: "Brand") -> str:
        if not brand.meta or not brand.meta.name:
            return "brand"

        return brand.meta.name.short or brand.meta.name.full or "brand"

    @staticmethod
    def _prepare_color_vars(
        brand: "Brand",
    ) -> tuple[dict[str, YamlScalarType], dict[str, YamlScalarType], list[str]]:
        """
        Colors: Create a dictionaries of Sass and CSS variables
        """
        if not brand.color:
            return {}, {}, []

        defaults_dict: dict[str, YamlScalarType] = {}
        palette_defaults_dict: dict[str, YamlScalarType] = {}
        palette_css_vars: list[str] = []

        for thm_name, thm_color in brand.color.to_dict(include="theme").items():
            # Create brand Sass variables and set related Bootstrap Sass vars
            # brand.color.primary = "#007bff"
            # ==> $brand_color_primary: #007bff !default;
            # ==> $primary: $brand_color_primary !default;

            brand_color_var = f"brand_color_{thm_name}"
            defaults_dict[brand_color_var] = thm_color

        brand_color_palette = brand.color.to_dict(include="palette")

        # Map the brand color palette to Bootstrap's named colors, e.g. $red, $blue.
        for pal_name, pal_color in brand_color_palette.items():
            if pal_name in bootstrap_colors:
                defaults_dict[pal_name] = pal_color

            # Create Sass and CSS variables for the brand color palette
            # => Sass var: `$brand-{name}: {value}`
            palette_defaults_dict.update({f"brand-{pal_name}": pal_color})
            # => CSS var: `--brand-{name}: {value}`
            palette_css_vars.append(f"  --brand-{pal_name}: {pal_color};")

        palette_rules = [
            "// *---- brand.color.palette ----* //",
            ":root {",
            *palette_css_vars,
            "}",
        ]

        return (
            palette_defaults_dict,  # brand.color.palette:defaults
            defaults_dict,  # brand.color:defaults
            palette_rules,  # brand.color.palette:rules
        )

    @staticmethod
    def _prepare_typography_vars(brand: "Brand") -> dict[str, YamlScalarType]:
        """
        Typography: Create a list of brand Sass variables

        Creates a dictionary of Sass variables for typography settings defined in the
        `brand` object. These are used to set brand Sass variables in the format
        `$brand_typography_{field}_{prop}`, for example:

        ```scss
        $brand_typography_base_size: 16rem;
        $brand_typography_base_line-height: 1.25;
        ```
        """
        mapped: dict[str, YamlScalarType] = {}

        if not brand.typography:
            return mapped

        brand_typography = brand.typography.model_dump(
            exclude={"fonts"},
            exclude_none=True,
            context={"typography_base_size_unit": "rem"},
        )

        for field, prop in brand_typography.items():
            for prop_key, prop_value in prop.items():
                typo_sass_var = f"brand_typography_{field}_{prop_key}"
                mapped[typo_sass_var] = prop_value

        return mapped

    def _add_defaults_hdr(self, header: str, **kwargs: YamlScalarType):
        self.add_defaults(**kwargs)
        self.add_defaults(f"\n// *---- brand: {header} ----* //")

    def _add_brand_bootstrap_other(self, bootstrap: BrandBootstrapConfig):
        if bootstrap.functions:
            self.add_functions(
                *[
                    "// *---- brand.defaults: bootstrap.functions ----* //",
                    bootstrap.functions,
                ]
            )
        if bootstrap.mixins:
            self.add_mixins(
                *[
                    "// *---- brand.defaults: bootstrap.mixins ----* //",
                    bootstrap.mixins,
                ]
            )
        if bootstrap.rules:
            self.add_rules(
                *["// *---- brand.defaults: bootstrap.rules ----* //", bootstrap.rules]
            )

    def _html_dependencies(self) -> list[HTMLDependency]:
        theme_deps = super()._html_dependencies()

        if not self.brand.typography:
            return theme_deps

        # We're going to put the fonts dependency _inside_ the theme's tempdir, which
        # relies on the theme's dependency having `all_files=True`. We do this because
        # Theme handles the tempdir lifecycle and we want the fonts dependency to be
        # handled in the same way.
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
