"""
Regression guards for https://github.com/posit-dev/py-shiny/issues/1635

When `ui.input_dark_mode()` is combined with `@render.data_frame` and
`render.DataGrid()`, the column header (and hovered row) background must
stay readable. The fix routes `--shiny-datagrid-grid-header-bgcolor` (and
related tokens) through Bootstrap 5.3 mode-aware variables so the surface
darkens under `data-bs-theme="dark"`. These tests assert the resulting
luminance and WCAG contrast so we don't regress that wiring.
"""

from __future__ import annotations

from playwright.sync_api import Page, expect

from shiny.playwright import controller
from shiny.run import ShinyAppProc


def _parse_rgb(color: str) -> tuple[float, float, float]:
    """Parse a CSS `rgb(...)`/`rgba(...)` string into a 0-1 RGB tuple."""
    inner = color[color.index("(") + 1 : color.index(")")]
    parts = [p.strip() for p in inner.split(",")]
    r, g, b = (float(parts[0]), float(parts[1]), float(parts[2]))
    return (r / 255.0, g / 255.0, b / 255.0)


def _relative_luminance(color: str) -> float:
    """Compute WCAG relative luminance for a CSS color string."""

    def _channel(c: float) -> float:
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = _parse_rgb(color)
    return 0.2126 * _channel(r) + 0.7152 * _channel(g) + 0.0722 * _channel(b)


def _contrast_ratio(fg: str, bg: str) -> float:
    l1 = _relative_luminance(fg)
    l2 = _relative_luminance(bg)
    lighter, darker = max(l1, l2), min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def _resolved_var(page: Page, selector: str, var_name: str) -> str:
    """Get the resolved value of a CSS custom property, as a real rgb() color."""
    return page.evaluate(
        """([selector, varName]) => {
            const el = document.querySelector(selector);
            const raw = getComputedStyle(el).getPropertyValue(varName).trim();
            // Resolve the variable into a concrete color by applying it as a
            // background on a probe element and reading back computedStyle.
            const probe = document.createElement('div');
            probe.style.background = raw;
            document.body.appendChild(probe);
            const resolved = getComputedStyle(probe).backgroundColor;
            probe.remove();
            return resolved;
        }""",
        [selector, var_name],
    )


def test_data_grid_header_readable_in_dark_mode(
    page: Page, local_app: ShinyAppProc
) -> None:
    page.emulate_media(color_scheme="dark")
    page.goto(local_app.url)

    mode_switch = controller.InputDarkMode(page, "mode")
    mode_switch.expect_mode("dark")

    grid = page.locator("#grid")
    expect(grid.locator("table thead th").first).to_be_visible()

    header_bg = _resolved_var(
        page, "shiny-data-frame", "--shiny-datagrid-grid-header-bgcolor"
    )
    header_th = grid.locator("table thead tr:first-child th").first
    header_color = header_th.evaluate(
        "el => getComputedStyle(el).color"
    )

    # In dark mode the header background should itself be dark — the fix
    # routes it through `--bs-tertiary-bg`, which flips with the theme.
    header_bg_luminance = _relative_luminance(header_bg)
    assert header_bg_luminance < 0.5, (
        f"Header background {header_bg!r} is too light for dark mode "
        f"(luminance={header_bg_luminance:.3f})"
    )

    # And whatever the background ends up being, header text must be readable.
    contrast = _contrast_ratio(header_color, header_bg)
    assert contrast >= 4.5, (
        f"Header text contrast is too low in dark mode: "
        f"color={header_color!r}, bg={header_bg!r}, ratio={contrast:.2f}"
    )


def test_data_grid_row_hover_readable_in_dark_mode(
    page: Page, local_app: ShinyAppProc
) -> None:
    page.emulate_media(color_scheme="dark")
    page.goto(local_app.url)

    mode_switch = controller.InputDarkMode(page, "mode")
    mode_switch.expect_mode("dark")

    grid = page.locator("#grid")
    first_row_cell = grid.locator("table tbody tr:first-child td").first
    expect(first_row_cell).to_be_visible()

    first_row_cell.hover()

    hover_bg = first_row_cell.evaluate(
        "el => getComputedStyle(el.parentElement).backgroundColor"
    )
    # Some browsers report transparent on the <tr> when the rule targets <td>.
    if hover_bg in ("rgba(0, 0, 0, 0)", "transparent"):
        hover_bg = first_row_cell.evaluate(
            "el => getComputedStyle(el).backgroundColor"
        )
    cell_color = first_row_cell.evaluate("el => getComputedStyle(el).color")

    hover_bg_luminance = _relative_luminance(hover_bg)
    assert hover_bg_luminance < 0.5, (
        f"Hovered row background {hover_bg!r} is too light for dark mode "
        f"(luminance={hover_bg_luminance:.3f})"
    )

    contrast = _contrast_ratio(cell_color, hover_bg)
    assert contrast >= 4.5, (
        f"Hovered row contrast is too low in dark mode: "
        f"color={cell_color!r}, bg={hover_bg!r}, ratio={contrast:.2f}"
    )
