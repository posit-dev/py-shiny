"""A deterministic sales planning app used to record the static reactlog demo."""

from matplotlib.figure import Figure
from shiny import App, reactive, render, ui

from scenario import scenario_server, scenario_ui

app_ui = ui.page_fluid(
    ui.h2("Northstar · Revenue & inventory planning"),
    ui.p(
        "Compare a baseline with a promotional campaign, then review the combined plan. Demo data."
    ),
    ui.layout_columns(
        ui.input_slider("horizon", "Forecast horizon (weeks)", 4, 16, 8),
        ui.input_numeric("fixed_cost", "Weekly overhead ($)", 1800, min=0),
        ui.input_numeric("target", "Profit target ($)", 25000, min=0),
        col_widths=(6, 3, 3),
    ),
    ui.layout_columns(
        scenario_ui("baseline", "Baseline channel"),
        scenario_ui("campaign", "Campaign channel"),
    ),
    ui.card(
        ui.card_header("Portfolio outlook"),
        ui.output_text("portfolio_summary"),
        ui.output_text("target_status"),
        ui.output_plot("portfolio_plot", height="260px"),
    ),
    title="Northstar planning demo",
)


def server(input, output, session):
    @reactive.calc
    def weeks():
        return input.horizon()

    baseline = scenario_server("baseline", weeks)
    campaign = scenario_server("campaign", weeks)

    @reactive.calc
    def portfolio():
        return [
            {
                "week": a["week"],
                "revenue": a["revenue"] + b["revenue"],
                "profit": a["profit"] + b["profit"] - input.fixed_cost(),
            }
            for a, b in zip(baseline(), campaign())
        ]

    @reactive.calc
    def total_profit():
        return sum(row["profit"] for row in portfolio())

    @render.text
    def portfolio_summary():
        return f"{weeks()}-week revenue: ${sum(r['revenue'] for r in portfolio()):,.0f} · Net profit: ${total_profit():,.0f}"

    @render.text
    def target_status():
        gap = total_profit() - input.target()
        return f"{'Above' if gap >= 0 else 'Below'} target by ${abs(gap):,.0f}"

    @render.plot
    def portfolio_plot():
        rows = portfolio()
        fig = Figure(figsize=(11, 2.7), layout="constrained")
        ax = fig.subplots()
        ax.bar([r["week"] for r in rows], [r["profit"] for r in rows], color="#6366f1")
        ax.axhline(
            input.target() / weeks(),
            color="#d97706",
            linestyle="--",
            label="Weekly profit target",
        )
        ax.set(xlabel="Week", ylabel="Net profit ($)")
        ax.legend(frameon=False)
        return fig


app = App(app_ui, server)
