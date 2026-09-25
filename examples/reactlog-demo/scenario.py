"""Reusable sales scenario UI and server module."""

from matplotlib.figure import Figure
from shiny import module, reactive, render, ui


@module.ui
def scenario_ui(title):
    return ui.card(
        ui.card_header(title),
        ui.layout_columns(
            ui.input_numeric("units", "Weekly units", 160, min=10, max=1000),
            ui.input_numeric("price", "Unit price ($)", 45, min=1),
            ui.input_numeric("cost", "Unit cost ($)", 24, min=1),
            col_widths=(4, 4, 4),
        ),
        ui.input_slider("growth", "Weekly demand growth (%)", -5, 15, 3),
        ui.input_action_button("apply_discount", "Toggle 10% promotion"),
        ui.output_text("summary"),
        ui.output_plot("revenue_plot", height="230px"),
    )


@module.server
def scenario_server(input, output, session, weeks):
    @reactive.calc
    def discount_multiplier():
        return 0.9 if input.apply_discount() % 2 else 1.0

    @reactive.calc
    def subtotal():
        return input.units() * input.price()

    @reactive.calc
    def total_revenue():
        return subtotal() * discount_multiplier()

    @reactive.calc
    def forecast():
        revenue = total_revenue()
        growth = input.growth() / 100
        cost = input.units() * input.cost()
        return [
            {
                "week": week + 1,
                "revenue": revenue * (1 + growth) ** week,
                "profit": (revenue - cost) * (1 + growth) ** week,
            }
            for week in range(weeks())
        ]

    @render.text
    def summary():
        rows = forecast()
        return f"Weekly sales: ${total_revenue():,.0f} · Forecast profit: ${sum(r['profit'] for r in rows):,.0f}"

    @render.plot
    def revenue_plot():
        rows = forecast()
        fig = Figure(figsize=(6, 2.6), layout="constrained")
        ax = fig.subplots()
        ax.plot(
            [r["week"] for r in rows],
            [r["revenue"] for r in rows],
            color="#0284c7",
            marker="o",
            label="Revenue",
        )
        ax.plot(
            [r["week"] for r in rows],
            [r["profit"] for r in rows],
            color="#16a34a",
            label="Profit",
        )
        ax.set(xlabel="Week", ylabel="Dollars")
        ax.legend(frameon=False)
        ax.grid(alpha=0.15)
        return fig

    return forecast
