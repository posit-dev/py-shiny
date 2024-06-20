from __future__ import annotations

import os
import pathlib
import tempfile
import textwrap
from typing import (
    Any,
    Callable,
    Iterable,
    Literal,
    Optional,
    Sequence,
    TypeVar,
    Union,
    cast,
)

from htmltools import HTMLDependency
from packaging.version import Version

from .._docstring import no_example
from .._typing_extensions import NotRequired, TypedDict
from .._versions import bootstrap
from ._theme_presets import (
    ShinyThemePreset,
    shiny_theme_presets,
    shiny_theme_presets_bundled,
)
from ._utils import path_pkg_www

T = TypeVar("T", bound="Theme")


SassImporterReturnValue = Union["tuple[str]", "tuple[str, str]", "tuple[str, str, str]"]
SassImporterFunction = Union[
    Callable[[str], SassImporterReturnValue],
    Callable[[str, str], SassImporterReturnValue],
]


class SassCompileArgs(TypedDict):
    output_style: NotRequired[Literal["nested", "expanded", "compact", "compressed"]]
    source_comments: NotRequired[bool]
    source_map_contents: NotRequired[bool]
    source_map_embed: NotRequired[bool]
    omit_source_map_url: NotRequired[bool]
    source_map_root: NotRequired[str | None]
    include_paths: NotRequired[Sequence[str]]
    precision: NotRequired[int]
    custom_functions: NotRequired[Any]  # not worth the effort, it's a complicated type
    indented: NotRequired[bool]
    importers: NotRequired[Iterable[tuple[int, SassImporterFunction]] | None]


@no_example()
class Theme:
    """
    Create a custom Shiny theme.

    The `Theme` class allows you to create a custom Shiny theme by providing custom Sass
    code. The theme can be based on one of the available presets, such as `"shiny"` or
    `"bootstrap"`, or a Bootswatch theme. Use the `.add_*()` methods can be chained
    together to add custom Sass functions, defaults, mixins, and rules.

    Pass the `Theme` object directly to the `theme` argument of any Shiny page function,
    such as :func:`~shiny.ui.page_sidebar` or :func:`~shiny.ui.page_navbar`. In Shiny
    Express apps, use the `theme` argument of :func:`~shiny.express.ui.page_opts` to set
    the app theme.

    **Note: Compiling custom themes requires the
    [libsass](https://pypi.org/project/libsass/) package**, which is not installed by
    default with Shiny. Use `pip install libsass` or `pip install shiny[theme]` to
    install it.

    Customized themes are compiled to CSS when the theme is used. The `Theme` class
    caches the compiled CSS so that it's only compiled for the first user to load your
    app, but you can speed up app loading (and avoid the runtime `libsass` dependency)
    by pre-compiling the theme CSS and saving it to a file. To do this, use the
    `.to_css()` method to render the theme to a single minified CSS string. Once saved
    to a file, the CSS can be used in any Shiny app by passing the file path to the
    `theme` argument instead of the `Theme` object.

    ```{.python filename="my_theme.py"}
    from shiny import ui

    my_theme = (
        ui.Theme("shiny")
        .add_mixins(
            headings_color="$success",
            bar_color="$purple",
            select_color_text="$orange",
        )
    )

    with open("my_theme.css", "w") as f:
        f.write(my_theme.to_css())
    ```

    ```{.python filename="app.py"}
    from shiny import ui

    ui = ui.page_fluid(
        # App content...
        title="My App",
        theme="my_theme.css",
    )
    ```

    Parameters
    ----------
    preset
        The name of the preset to use as a base. `"shiny"` is the default theme for
        Shiny apps and `"bootstrap"` uses standard Bootstrap 5 styling. Bootswatch theme
        presets are also available. Use `Theme.available_presets()` to see the full
        list.
    name
        A custom name for the theme. If not provided, the preset name will be used.
    include_paths
        Additional paths to include when looking for Sass files used in `@import`
        statements in the theme. This can be a single path as a string or
        :class:`pathlib.Path`, or a list of paths. The paths should point to directories
        containing additional Sass files that the theme depends on.

    Raises
    ------
    ValueError
        If the `preset` is not a valid theme preset.
    """

    def __init__(
        self,
        preset: ShinyThemePreset = "shiny",
        name: Optional[str] = None,
        include_paths: Optional[str | pathlib.Path | list[str | pathlib.Path]] = None,
    ):
        check_is_valid_preset(preset)
        self._preset: ShinyThemePreset = preset
        self.name = name
        self._version = bootstrap
        self._include_paths: list[str] = []

        if isinstance(include_paths, (str, pathlib.Path)):
            self._include_paths.append(str(include_paths))
        elif isinstance(include_paths, Sequence):
            for path in include_paths:
                self._include_paths.append(str(path))

        # User-provided Sass code
        self._functions: list[str] = []
        self._defaults: list[str] = []
        self._mixins: list[str] = []
        self._rules: list[str] = []

        # _css is either:
        # 1. "" indicating that the CSS has not been compiled yet
        # 2. A string containing the compiled CSS for the current theme
        self._css: str = ""

        # If the theme has been customized and rendered once, we store the tempdir
        # so that we can re-use the already compiled CSS file.
        self._css_temp_srcdir: Optional[tempfile.TemporaryDirectory[str]] = None

    @staticmethod
    def available_presets() -> tuple[ShinyThemePreset, ...]:
        """
        Get a list of available theme presets.
        """
        return shiny_theme_presets

    @property
    def preset(self) -> ShinyThemePreset:
        return self._preset

    @preset.setter
    def preset(self, value: ShinyThemePreset) -> None:
        check_is_valid_preset(value)
        self._preset = value
        self._reset_css()

    def _reset_css(self) -> None:
        self._css = ""
        if self._css_temp_srcdir is not None:
            self._css_temp_srcdir.cleanup()
        self._css_temp_srcdir = None

    def _has_customizations(self) -> bool:
        return (
            len(self._functions) > 0
            or len(self._defaults) > 0
            or len(self._mixins) > 0
            or len(self._rules) > 0
        )

    def _can_use_precompiled(self) -> bool:
        return (
            self._preset in shiny_theme_presets_bundled
            and not self._has_customizations()
        )

    @staticmethod
    def _combine_args_kwargs(
        *args: str,
        allow_both: bool = True,
        kwargs: dict[str, str | float | int | bool | None],
        is_default: bool = False,
    ) -> list[str]:
        if not allow_both and len(args) > 0 and len(kwargs) > 0:
            # Python forces positional arguments to come _before_ kwargs, but default
            # argument order might matter. To be safe, we force users to pick one order.
            raise ValueError("Cannot provide both positional and keyword arguments.")
        if len(args) == 0 and len(kwargs) == 0:
            return []

        values: list[str] = list(args)
        default = " !default" if is_default else ""

        if len(kwargs) > 0:
            for key, value in kwargs.items():
                key = key.replace("_", "-")
                if isinstance(value, bool):
                    value = "true" if value else "false"
                elif value is None:
                    value = "null"
                values.append(f"${key}: {value}{default};")

        return [textwrap.dedent(x) for x in values]

    def add_functions(self: T, *args: str) -> T:
        """
        Add custom Sass functions to the theme.

        Sass code added via this method will be placed **after** the function
        declarations from the theme preset, allowing you to override or extend the
        default functions.

        Parameters
        ----------
        *args
            The Sass functions to add as a single or multiple strings.
        """
        functions = self._combine_args_kwargs(*args, kwargs={})
        self._functions.extend(functions)
        self._reset_css()
        return self

    def add_defaults(
        self: T,
        *args: str,
        **kwargs: str | float | int | bool | None,
    ) -> T:
        """
        Add custom default values to the theme.

        Sass code added via this method will be placed **before** the default values of
        the theme preset, allowing you to override or extend the default values.

        Parameters
        ----------
        *args
            Sass code, as a single or multiple strings, containing default value
            declarations to add.
        **kwargs
            Keyword arguments containing default value declarations to add. The keys
            should be Sass variable names using underscore casing that will be
            transformed automatically to kebab-case. For example,
            `.add_defaults(primary_color="#ff0000")` is equivalent to
            `.add_defaults("$primary-color: #ff0000 !default;")`.
        """
        defaults = self._combine_args_kwargs(
            *args,
            kwargs=kwargs,
            allow_both=False,
            is_default=True,
        )

        # Add args to the front of _defaults
        self._defaults[:0] = defaults
        self._reset_css()

        return self

    def add_mixins(
        self: T,
        *args: str,
        **kwargs: str | float | int | bool | None,
    ) -> T:
        """
        Add custom Sass mixins to the theme.

        Sass code added via this method will be placed **after** the mixin declarations
        from the theme preset, allowing you to override or extend the default mixins.

        Parameters
        ----------
        *args
            Sass code, as a single or multiple strings, containing mixins to add.
        **kwargs
            Keyword arguments containing Sass value declarations to add. The keys
            should be Sass variable names using underscore casing that will be
            transformed automatically to kebab-case. For example,
            `.add_mixins(primary_color="#ff0000")` is equivalent to
            `.add_mixins("$primary-color: #ff0000;")`.
        """
        mixins = self._combine_args_kwargs(*args, kwargs=kwargs)
        self._mixins.extend(mixins)
        self._reset_css()
        return self

    def add_rules(
        self: T,
        *args: str,
        **kwargs: str | float | int | bool | None,
    ) -> T:
        """
        Add custom Sass rules to the theme.

        Sass code added via this method will be placed **after** the rule declarations
        from the theme preset, allowing you to override or extend the default rules.

        Parameters
        ----------
        *args
            Sass code, as a single or multiple strings, containing rules to add.
        **kwargs
            Keyword arguments containing Sass value declarations to add. The keys
            should be Sass variable names using underscore casing that will be
            transformed automatically to kebab-case. For example,
            `.add_rules(primary_color="#ff0000")` is equivalent to
            `.add_rules("$primary-color: #ff0000;")`.
        """
        rules = self._combine_args_kwargs(*args, kwargs=kwargs)
        self._rules.extend(rules)
        self._reset_css()
        return self

    def to_sass(self) -> str:
        """
        Returns the custom theme as a single Sass string.

        Returns
        -------
        :
            The custom theme as a single Sass string.
        """
        path_functions = path_pkg_preset(self._preset, "_01_functions.scss")
        path_defaults = path_pkg_preset(self._preset, "_02_defaults.scss")
        path_mixins = path_pkg_preset(self._preset, "_03_mixins.scss")
        path_rules = path_pkg_preset(self._preset, "_04_rules.scss")

        sass_lines = [
            f'@import "{path_functions}";',
            *self._functions,
            *self._defaults,
            f'@import "{path_defaults}";',
            f'@import "{path_mixins}";',
            *self._mixins,
            f'@import "{path_rules}";',
            *self._rules,
        ]

        return "\n".join(sass_lines)

    def to_css(
        self,
        compile_args: Optional[SassCompileArgs] = None,
    ) -> str:
        """
        Compile the theme to CSS and return the result as a string.

        Parameters
        ----------
        compile_args
            A dictionary of keyword arguments to pass to :func:`sass.compile`.

        Returns
        -------
        :
            The compiled CSS for the theme. The value is cached such that previously
            compiled themes are returned immediately. Adding additional custom Sass code
            or changing the preset will invalidate the cache.
        """
        if self._css:
            return self._css

        if self._can_use_precompiled():
            self._css = self._read_precompiled_css()
            return self._css

        check_libsass_installed()
        import sass

        if compile_args is None:
            compile_args = {"output_style": "compressed"}

        self._css = cast(
            str,
            sass.compile(
                string=self.to_sass(),
                include_paths=self._include_paths,
                **compile_args,  # type: ignore
            ),
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

    def _html_dependency(self) -> HTMLDependency:
        """
        Create an `HTMLDependency` object from the theme.

        Returns
        -------
        :
            An :class:`~htmltools.HTMLDependency` object representing the theme. In
            most cases, you should not need to call this method directly. Instead, pass
            the `Theme` object directly to the `theme` argument of any Shiny page
            function.
        """
        if self._can_use_precompiled():
            return self._html_dependency_precompiled()

        dep_name = f"shiny-theme-{self.name or self._preset}"
        css_name = f"{dep_name}.min.css"

        # Re-use already compiled CSS file if possible
        if self._css and self._css_temp_srcdir is not None:
            return HTMLDependency(
                name=dep_name,
                version=Version(self._version),
                source={"subdir": self._css_temp_srcdir.name},
                stylesheet={"href": css_name},
            )

        srcdir = tempfile.TemporaryDirectory()
        css_path = os.path.join(srcdir.name, css_name)

        with open(css_path, "w") as css_file:
            css_file.write(self.to_css())

        self._css_temp_srcdir = srcdir
        return HTMLDependency(
            name=dep_name,
            version=Version(self._version),
            source={"subdir": srcdir.name},
            stylesheet={"href": css_name},
        )

    def tagify(self) -> None:
        raise SyntaxError(
            "The `Theme` class is not meant to be used as a standalone HTML tag. "
            "Instead, pass the `Theme` object directly to the `theme` argument of any "
            "Shiny page function.",
        )


def path_pkg_preset(preset: ShinyThemePreset, *args: str) -> str:
    """
    Returns a path relative to the packaged directory for a given preset.

    Examples
    --------

    ```python
    path_pkg_preset("shiny", "preset.min.css")
    #> "{shiny}/www/shared/sass/preset/shiny/preset.min.css"
    ```
    """
    return os.path.realpath(path_pkg_www("sass", "preset", str(preset), *args))


def check_is_valid_preset(preset: ShinyThemePreset) -> None:
    if preset not in shiny_theme_presets:
        raise ValueError(
            f"Invalid preset '{preset}'.\n"
            + f"""Expected one of: "{'", "'.join(shiny_theme_presets)}".""",
        )


def check_libsass_installed() -> None:
    import importlib.util

    if importlib.util.find_spec("sass") is None:
        raise ImportError(
            "The 'libsass' package is required to compile custom themes. "
            "Please install it with `pip install libsass` or `pip install shiny[theme]`.",
        )
