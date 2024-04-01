from __future__ import annotations

from pathlib import Path
from typing import Literal, Optional

from htmltools import HTMLDependency, Tag, Tagifiable, TagList
from packaging.version import Version

from ._include_helpers import include_css

__all__ = ("theme",)


class Theme:
    """
    A theme object for Shiny UI page elements.
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
            theme_tag = include_css(theme)
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
        self.name = name
        self.version = maybe_version(version, "version")
        self.bs_version = maybe_version(bs_version, "bs_version")
        self.replace = replace

    def __repr__(self) -> str:
        return (
            f"Theme(theme={self.theme!r}, name={self.name!r}, "
            + f"version={self.version!r}, bs_version={self.bs_version!r}, "
            + f"replace={self.replace!r})"
        )


def theme(
    theme: str | Path | Tag | Tagifiable,
    *,
    name: Optional[str] = None,
    version: Optional[str] = None,
    bs_version: Optional[str | Version] = None,
    replace: Literal["css", "all", "none"] = "css",
) -> Theme:
    """
    Create a theme object for Shiny UI page elements.

    Parameters
    ----------
    theme
        The theme to use. This can be a string or Path (interpreted as a path to a CSS
        file), a :class:`~htmltools.Tag`, or a :class:`~htmltools.Tagifiable`.
    name
        The name of the theme.
    version
        The version of the theme. (Not the version of Bootstrap used by the theme.)
    bs_version
        The Bootstrap version that the theme is compatible with.
    replace
        How this theme replaces Shiny's built-in Bootstrap theme. If ``"css"``, the CSS
        of this theme replaces the `bootstrap.min.css`. If ``"all"``, the entire
        Bootstrap bundle, including both `bootstrap.min.css` and `bootstrap.min.js`,
        is replaced. If ``"none"``, the Bootstrap bundle is not replaced and the theme
        dependency is added as additional CSS (and/or JavaScript) files.

    Returns
    -------
    :
        A theme object for Shiny UI page elements.
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
