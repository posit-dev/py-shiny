from __future__ import annotations

from shiny import reactive
from shiny.express import input, render, ui

ui.page_opts(title="Global Supply Chain & Revenue Analytics", fillable=True)

with ui.sidebar(title="Simulation Parameters"):
    ui.input_select(
        "region",
        "Target Region",
        ["North America", "Europe", "Asia-Pacific", "Latin America"],
        selected="North America",
    )
    ui.input_slider("discount_rate", "Promotional Discount (%)", 0, 40, 15)
    ui.input_slider("marketing_spend", "Marketing Budget ($k)", 10, 500, 120)
    ui.input_numeric("base_customers", "Baseline Audience", 5000, min=500, max=50000)
    ui.input_checkbox("enable_surge", "Apply Peak Surge Multiplier", value=True)


@reactive.calc
def regional_factor() -> float:
    region = input.region()
    multipliers = {
        "North America": 1.25,
        "Europe": 1.10,
        "Asia-Pacific": 1.40,
        "Latin America": 0.90,
    }
    return multipliers.get(region, 1.0)


@reactive.calc
def raw_demand() -> float:
    spend = input.marketing_spend()
    audience = input.base_customers()
    return float(audience * 0.08 + spend * 12.5)


@reactive.calc
def effective_conversion() -> float:
    demand = raw_demand()
    discount = input.discount_rate()
    discount_boost = 1.0 + (discount / 100.0) * 0.75
    return float(demand * discount_boost)


@reactive.calc
def gross_revenue() -> float:
    units = effective_conversion()
    reg_mult = regional_factor()
    avg_price = 85.0
    return float(units * avg_price * reg_mult)


@reactive.calc
def net_profit() -> float:
    rev = gross_revenue()
    spend = input.marketing_spend() * 1000.0
    cogs = rev * 0.42
    surge_bonus = 1.15 if input.enable_surge() else 1.0
    return float((rev * surge_bonus) - cogs - spend)


@reactive.calc
def inventory_risk() -> str:
    units = effective_conversion()
    surge = input.enable_surge()
    if units > 8000 and surge:
        return "HIGH RISK: Stockout probable within 14 days"
    elif units > 5000:
        return "MODERATE RISK: Buffer inventory recommended"
    return "LOW RISK: Stock levels optimal"


@reactive.effect
def alert_logger() -> None:
    risk = inventory_risk()
    if "HIGH" in risk:
        print(f"[ALERT] Supply chain warning triggered: {risk}")


with ui.layout_columns(col_widths=(4, 4, 4)):
    with ui.value_box(theme="primary"):
        "Gross Revenue"

        @render.text
        def kpi_revenue() -> str:
            return f"${gross_revenue():,.2f}"

    with ui.value_box(theme="success"):
        "Estimated Net Profit"

        @render.text
        def kpi_profit() -> str:
            return f"${net_profit():,.2f}"

    with ui.value_box(theme="warning"):
        "Inventory Status"

        @render.text
        def kpi_risk() -> str:
            return inventory_risk()


with ui.card():
    ui.card_header("Executive Forecast Summary")

    @render.text
    def forecast_summary() -> str:
        reg = regional_factor()
        conv = effective_conversion()
        prof = net_profit()
        return (
            f"Forecasted {conv:,.0f} units converted with regional index {reg:.2f}. "
            f"Projected net margin yield: ${prof:,.2f}."
        )
