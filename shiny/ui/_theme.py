from __future__ import annotations

from pathlib import Path
from typing import Literal, Optional
from warnings import warn

from htmltools import HTMLDependency, Tag, Tagifiable, TagList
from htmltools.tags import head
from packaging.version import Version

from .._versions import bootstrap as BOOTSTRAP_VERSION
from ._include_helpers import include_css

__all__ = ("theme",)


class Theme:
    """
    A theme for styling Shiny via the `theme` argument of page functions.

    Specify a theme that customizes the appearance of a Shiny application by replacing
    the default Bootstrap theme, by replacing Bootstrap altogether, or by layering on
    top of the default Bootstrap theme.

    Parameters
    ----------
    theme
        The theme to apply. This can be a path to a CSS file, a :class:`~htmltools.Tag`
        or :class:`~htmltools.Tagifiable` object, or an
        :class:`~htmltools.HTMLDependency`. When `theme` is a string or
        :class:`~pathlib.Path`, it is interpreted as a path to a CSS file that should
        completely replace `bootstrap.min.css`. The CSS file is included using
        :func:`~shiny.ui.include_css()`. For best results, the CSS file and its
        supporting assets should be stored in a subdirectory containing only the
        necessary files.
    name
        An optional name for the theme.
    version
        An optional version of the theme.
    bs_version
        The Bootstrap version with which the theme is compatible. When the theme is
        used, an error will be raised if the major version of Shiny's built-in Bootstrap
        version and does not match the theme's major Bootstrap version. Otherwise, a
        warning is raised if the minor or patch versions do not match.
    replace
        Specifies how the theme should replace existing styles:

        * `"css"` is the default: The theme replaces only the `bootstrap.min.css` file
          of Shiny's built-in Bootstrap theme.
        * `"none"`: The theme is added as additional CSS (and/or JavaScript) files in
          addition to Shiny's built-in Bootstrap theme.
        * `"all"`: Shiny's built-in Bootstrap theme is completely replaced by the theme.
          This option is for expert usage and should be used with caution. Shiny is
          designed to work with the currently bundled version of Bootstrap. Use the
          `bs_version` parameter to check compatibility of the provided theme with the
          bundled Bootstrap version at runtime.

    Attributes
    ----------
    theme
        The theme to apply as a tagified :class:`~htmltools.Tag`,
        :class:`~htmltools.TagList`, or :class:`~htmltools.HTMLDependency`.
    name
        An optional name for the theme.
    version
        An optional version of the theme.
    bs_version
        The Bootstrap version with which the theme is compatible.
    replace
        Specifies how the theme should replace existing styles:

        * `"css"` is the default: The theme replaces only the `bootstrap.min.css` file
          of Shiny's built-in Bootstrap theme.
        * `"none"`: The theme is added as additional CSS (and/or JavaScript) files in
          addition to Shiny's built-in Bootstrap theme.
        * `"all"`: Shiny's built-in Bootstrap theme is completely replaced by the theme.
          This option is for expert usage and should be used with caution. Shiny is
          designed to work with the currently bundled version of Bootstrap. Use the
          `bs_version` parameter to check compatibility of the provided theme with the
          bundled Bootstrap version at runtime.

    Raises
    ------
    ValueError
        If an invalid replacement strategy is specified for `replace`.
    TypeError
        If the theme, when tagified, does not return a `Tag` or `TagList`.
    """

    def __init__(
        self,
        theme: str | Path | Tag | Tagifiable | HTMLDependency,
        *,
        name: Optional[str] = None,
        version: Optional[str | Version] = None,
        bs_version: Optional[str | Version] = None,
        replace: Literal["css", "all", "none"] = "css",
    ) -> None:
        if replace not in ("css", "all", "none"):
            raise ValueError(
                f"Invalid value for `replace`: '{replace}'. "
                + "Must be one of 'css', 'all', 'none'."
            )

        if isinstance(theme, (str, Path)):
            theme_tag = head(include_css(theme))
        elif isinstance(theme, HTMLDependency):
            theme_tag = theme
        else:
            theme_tag = theme.tagify()

            if not isinstance(theme_tag, (Tag, TagList)):
                raise TypeError(
                    f"Invalid tagified type for `theme`: {type(theme_tag)}. "
                    + "When tagified, `theme` must return a `Tag` or `TagList`."
                )

        self.theme: Tag | TagList | HTMLDependency = theme_tag
        self.name: Optional[str] = name
        self.version: Optional[Version] = maybe_version(version, "version")
        self.bs_version: Optional[Version] = maybe_version(bs_version, "bs_version")
        self.replace: Literal["css", "all", "none"] = replace

    def __repr__(self) -> str:
        return (
            f"Theme(theme={self.theme!r}, name={self.name!r}, "
            + f"version={self.version!r}, bs_version={self.bs_version!r}, "
            + f"replace={self.replace!r})"
        )

    def check_compatibility(
        self,
        base_version: str | Version = BOOTSTRAP_VERSION,
    ) -> None:
        """
        Checks the compatibility of the theme's Bootstrap version with the base version.

        This method compares the major version of the theme's Bootstrap version
        (`bs_version`) with the provided `base_version`. If the major versions are
        different, it raises a `RuntimeError` indicating that the versions are
        incompatible. If the major versions are the same but the versions are not
        identical, it issues a warning about the potential for unexpected issues due to
        the version mismatch.

        Parameters
        ----------
        base_version
            The base Bootstrap version to compare against. Defaults to the version of
            Bootstrap bundled with Shiny.

        Raises
        ------
        RuntimeError
            When the major versions of `bs_version` and `base_version` are different,
            indicating incompatibility between the theme's Bootstrap version and the
            base version.

        Warns
        -----
        RuntimeWarning
            When the versions are not identical but the major versions match, indicating
            a potential for unexpected issues.
        """
        if self.bs_version is None:
            return

        if not isinstance(base_version, Version):
            base_version = Version(base_version)

        if self.bs_version == base_version:
            return

        the_theme = f"'{self.name}'" if self.name else ""
        the_theme += f" ({self.version})" if self.version else ""
        the_theme = f"theme {the_theme}" if the_theme else "`theme`"

        if self.bs_version.major != base_version.major:
            raise RuntimeError(
                "Bootstrap version mismatch:"
                + f"\n  * {self.bs_version} from {the_theme}."
                + f"\n  * {base_version} from Shiny."
                + "\n  ! These versions of Bootstrap are incompatible."
            )

        warn(
            "Bootstrap version mismatch:"
            + f"\n  * {self.bs_version} from {the_theme}."
            + f"\n  * {base_version} from Shiny."
            + "\n  ! This version mismatch may cause unexpected issues.",
            RuntimeWarning,
        )


def theme(
    theme: str | Path | Tag | Tagifiable | HTMLDependency,
    *,
    name: Optional[str] = None,
    version: Optional[str] = None,
    bs_version: Optional[str | Version] = None,
    replace: Literal["css", "all", "none"] = "css",
) -> Theme:
    """
    A theme for styling Shiny.

    Specify a theme that customizes the appearance of a Shiny application by replacing
    the default Bootstrap theme, by replacing Bootstrap altogether, or by layering on
    top of the default Bootstrap theme.

    Parameters
    ----------
    theme
        The theme to apply. This can be a path to a CSS file, a :class:`~htmltools.Tag`
        or :class:`~htmltools.Tagifiable` object, or an
        :class:`~htmltools.HTMLDependency`. When `theme` is a string or
        :class:`~pathlib.Path`, it is interpreted as a path to a CSS file that should
        completely replace `bootstrap.min.css`. The CSS file is included using
        :func:`~shiny.ui.include_css()`. For best results, the CSS file and its
        supporting assets should be stored in a subdirectory containing only the
        necessary files.
    name
        An optional name for the theme.
    version
        An optional version of the theme.
    bs_version
        The Bootstrap version with which the theme is compatible. When the theme is
        used, an error will be raised if the major version of Shiny's built-in Bootstrap
        version and does not match the theme's major Bootstrap version. Otherwise, a
        warning is raised if the minor or patch versions do not match.
    replace
        Specifies how the theme should replace existing styles:

        * `"css"` is the default: The theme replaces only the `bootstrap.min.css` file
          of Shiny's built-in Bootstrap theme.
        * `"none"`: The theme is added as additional CSS (and/or JavaScript) files in
          addition to Shiny's built-in Bootstrap theme.
        * `"all"`: Shiny's built-in Bootstrap theme is completely replaced by the theme.
          This option is for expert usage and should be used with caution. Shiny is
          designed to work with the currently bundled version of Bootstrap. Use the
          `bs_version` parameter to check compatibility of the provided theme with the
          bundled Bootstrap version at runtime.

    Returns
    -------
    :
        A theme object for use with the `theme` argument of Shiny UI page elements.
    """
    return Theme(
        theme,
        name=name,
        version=version,
        bs_version=bs_version,
        replace=replace,
    )


def maybe_version(
    version: Optional[str | Version],
    name: str = "version",
) -> Optional[Version]:
    if version is None:
        return None

    if not isinstance(version, (str, Version)):
        raise TypeError(
            f"Invalid type for `{name}`: {type(version)}. "
            + "Must be a string or `packaging.version.Version`."
        )

    if isinstance(version, str):
        try:
            version = Version(version)
        except ValueError:
            raise ValueError(
                f"Invalid version string for `{name}`: '{version}'. "
                + "Must be a valid version string."
            )

    return version
