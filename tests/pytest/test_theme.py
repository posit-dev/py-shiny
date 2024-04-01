import pytest
from htmltools import HTMLDependency

from shiny import ui
from shiny._versions import bootstrap

v_bs = bootstrap.split(".")


def test_theme_incompatible_error():
    with pytest.raises(RuntimeError, match=r"Bootstrap version mismatch"):
        ui.theme(
            HTMLDependency("my-theme", "0.1.2"),
            bs_version="4.2.0",
            name="My Theme",
            version="0.1.2",
        ).check_compatibility()


def test_theme_incompatible_warning() -> None:
    theme_v_bs = f"{v_bs[0]}.{int(v_bs[1]) + 1}.0"

    with pytest.warns(RuntimeWarning, match=r"Bootstrap version mismatch"):
        ui.theme(
            HTMLDependency("my-theme", "0.1.2"),
            bs_version=theme_v_bs,
            name="My Theme",
            version=theme_v_bs,
        ).check_compatibility()

    with pytest.warns(RuntimeWarning, match=r"Bootstrap version mismatch"):
        ui.theme(
            HTMLDependency("name", "1.2.3"),
            bs_version="5.1.2",
            name="My Theme",
            version="0.1.0",
        ).check_compatibility("5.2.3")
