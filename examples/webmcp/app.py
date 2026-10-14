import json

from shiny import App, Inputs, Outputs, Session, reactive, render, ui, webmcp

REGIONS = ["All", "North", "South", "West"]
CHANNELS = ["All", "Online", "Retail"]

# Fictional orders, kept small enough to check the agent's answers by hand.
ORDERS = [
    ("North", "Online", 200),
    ("North", "Retail", 100),
    ("South", "Online", 150),
    ("South", "Retail", 450),
    ("West", "Online", 360),
    ("West", "Online", 240),
    ("West", "Retail", 120),
    ("West", "Retail", 180),
]

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_select("region", "Region", REGIONS),
        ui.input_select("channel", "Channel", CHANNELS),
        ui.p("Fictional sales data. All amounts are in USD."),
    ),
    ui.h2("Explore together"),
    ui.p(
        "Change the filters yourself, or ask a browser agent: ",
        ui.em(
            "Compare West online sales with retail, and leave the dashboard "
            "showing online sales."
        ),
    ),
    ui.card(ui.card_header("Sales summary"), ui.output_text("headline")),
    ui.card(ui.card_header("Matching orders"), ui.output_ui("orders")),
    ui.card(
        ui.card_header("Structured result shared with the agent"),
        ui.tags.pre(ui.output_text("summary", inline=True)),
    ),
    title="Shiny + WebMCP sales explorer",
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.calc
    def sales():
        region, channel = input.region(), input.channel()
        if region not in REGIONS or channel not in CHANNELS:
            return {"error": "Choose a listed region and channel."}
        amounts = [
            amount
            for r, c, amount in ORDERS
            if (region == "All" or r == region) and (channel == "All" or c == channel)
        ]
        return {
            "filters": {"region": region, "channel": channel},
            "orders": len(amounts),
            "revenue": sum(amounts),
            "average_order": sum(amounts) / len(amounts) if amounts else None,
            "currency": "USD",
        }

    @render.text
    def headline():
        result = sales()
        if "error" in result:
            return result["error"]
        return f"{result['orders']} orders · ${result['revenue']:,} USD"

    @render.ui
    def orders():
        result = sales()
        if "error" in result:
            return ui.p(result["error"])
        return ui.tags.table(
            ui.tags.thead(
                ui.tags.tr(
                    *(ui.tags.th(label) for label in ["Region", "Channel", "USD"])
                )
            ),
            ui.tags.tbody(
                *(
                    ui.tags.tr(ui.tags.td(r), ui.tags.td(c), ui.tags.td(f"${amount:,}"))
                    for r, c, amount in ORDERS
                    if (input.region() == "All" or r == input.region())
                    and (input.channel() == "All" or c == input.channel())
                )
            ),
            class_="table",
        )

    @render.text
    def summary():
        return json.dumps(sales(), indent=2)

    @webmcp.tool(
        description="Compare online and retail revenue for a region using fictional sales data. Returns both totals in USD and their difference without changing the dashboard.",
        input_schema={
            "type": "object",
            "properties": {"region": {"type": "string", "enum": REGIONS}},
            "required": ["region"],
            "additionalProperties": False,
        },
        read_only=True,
    )
    def compare_channels(region: str):
        totals = {
            channel: sum(
                amount
                for r, c, amount in ORDERS
                if (region == "All" or region == r) and c == channel
            )
            for channel in ["Online", "Retail"]
        }
        return {
            "region": region,
            "currency": "USD",
            **totals,
            "online_minus_retail": totals["Online"] - totals["Retail"],
        }


app = App(app_ui, server, webmcp=True)
