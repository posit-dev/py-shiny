from __future__ import annotations

import os
import tempfile
from textwrap import dedent
from typing import Optional, TypeVar

from htmltools import HTMLDependency
from packaging.version import Version

from .._docstring import no_example
from .._versions import bootstrap
from ._theme_presets import (
    ShinyThemePreset,
    ShinyThemePresets,
    ShinyThemePresetsBundled,
)
from ._utils import path_pkg_www

T = TypeVar("T", bound="Theme")


@no_example()
class Theme:
    def __init__(
        self,
        preset: ShinyThemePreset = "shiny",
        name: Optional[str] = None,
    ):
        check_is_valid_preset(preset)
        self._preset: ShinyThemePreset = preset
        self.name = name
        self._version = bootstrap

        # User-provided Sass code
        self._functions: list[str] = []
        self._defaults: list[str] = []
        self._mixins: list[str] = []
        self._rules: list[str] = []

        # _css is either:
        # 1. "precompiled" indicating it's okay to use precompiled preset.min.css
        # 2. "" indicating that the CSS has not been compiled yet
        # 3. A string containing the compiled CSS for the current theme
        self._css: str = "precompiled" if preset in ShinyThemePresetsBundled else ""

        # If the theme has been customized and rendered once, we store the tempdir
        # so that we can re-use the already compiled CSS file.
        self._css_temp_srcdir: Optional[str] = None

    @property
    def preset(self) -> ShinyThemePreset:
        return self._preset

    @preset.setter
    def preset(self, value: ShinyThemePreset) -> None:
        check_is_valid_preset(value)
        self._preset = value

        if self._css != "precompiled":
            self._css = ""
        self._css_temp_srcdir = None

    def add_functions(self: T, *args: list[str]) -> T:
        self._css = ""
        self._functions.extend(dedent_array(*args))
        return self

    def add_defaults(self: T, *args: str, **kwargs: dict[str, str]) -> T:
        if len(args) > 0 and len(kwargs) > 0:
            raise ValueError("Cannot provide both positional and keyword arguments")

        defaults: list[str] = list(args)

        if len(kwargs) > 0:
            for key, value in kwargs.items():
                key.replace("_", "-")
                if isinstance(value, bool):
                    value = "true" if value else "false"
                defaults.append(f"${key}: {value};")

        # Add args to the front of _defaults
        self._defaults = dedent_array(defaults) + self._defaults
        self._css = ""

        return self

    def add_mixins(self: T, *args: str) -> T:
        self._mixins.extend(dedent_array(args))
        self._css = ""
        return self

    def add_rules(self: T, *args: str) -> T:
        self._rules.extend(dedent_array(args))
        self._css = ""
        return self

    def to_css(self) -> str:
        if self._css:
            if self._css == "precompiled":
                return self._read_precompiled_css()
            return self._css

        check_libsass_installed()
        import sass

        sass_lines = [
            '@import "_01_functions";',
            *self._functions,
            *self._defaults,
            '@import "_02_defaults";',
            '@import "_03_mixins";',
            *self._mixins,
            '@import "_04_rules";',
            *self._rules,
        ]

        sass_string = "\n".join(sass_lines)

        self._css = sass.compile(
            string=sass_string,
            include_paths=[path_pkg_preset(self._preset)],
        )

        return self._css

    def _read_precompiled_css(self) -> str:
        path = path_pkg_preset(self._preset, "preset.min.css")
        with open(path, "r") as f:
            return f.read()

    def _html_dependency_precompiled(self) -> HTMLDependency:
        return HTMLDependency(
            name=f"shiny-theme-{self._preset}",
            version=self._version,
            source={
                "package": "shiny",
                "subdir": f"www/shared/sass/preset/{self._preset}",
            },
            stylesheet={"href": "preset.min.css"},
            all_files=False,
        )

    def html_dependency(self) -> HTMLDependency:
        if self._css == "precompiled":
            return self._html_dependency_precompiled()

        dep_name = f"shiny-theme-{self.name or self._preset}"
        css_name = f"{dep_name}.min.css"

        # Re-use already compiled CSS file if possible
        if self._css_temp_srcdir is not None:
            return HTMLDependency(
                name=dep_name,
                version=Version(self._version),
                source={"subdir": self._css_temp_srcdir},
                stylesheet={"href": css_name},
            )

        tmpdir = tempfile.mkdtemp()
        srcdir = os.path.join(tmpdir, dep_name)
        os.mkdir(srcdir)
        css_path = os.path.join(srcdir, css_name)

        with open(os.path.join(srcdir, css_path), "w") as css_file:
            css_file.write(self.to_css())

        self._css_temp_srcdir = srcdir
        return HTMLDependency(
            name=dep_name,
            version=Version(self._version),
            source={"subdir": srcdir},
            stylesheet={"href": css_name},
        )

    def tagify(self) -> HTMLDependency:
        """
        Create an `HTMLDependency` object from the theme.
        """
        return self.html_dependency()


def dedent_array(x: list[str] | tuple[str, ...]) -> list[str]:
    return [dedent(y) for y in x]


def path_pkg_preset(preset: ShinyThemePreset, *args: str) -> str:
    return path_pkg_www("sass", "preset", str(preset), *args)


def check_is_valid_preset(preset: ShinyThemePreset) -> None:
    if preset not in ShinyThemePresets:
        raise ValueError(
            f"Invalid preset '{preset}'.\n"
            + f"""Expected one of: "{'", "'.join(ShinyThemePresets)}".""",
        )


def check_libsass_installed() -> None:
    import importlib.util

    if importlib.util.find_spec("sass") is None:
        raise ImportError(
            "The 'libsass' package is required to compile custom themes. "
            "Please install it with `pip install libsass` or `pip install shiny[theme]`.",
        )
