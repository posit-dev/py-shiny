import json

import plotly.express as px
import snowflake.snowpark.functions as F
from shinywidgets import output_widget, render_widget
from snowflake.snowpark.session import Session

from shiny import App, Inputs, Outputs, Session, reactive, ui

# create a snowpark session
with open("creds.json") as f:
    connection_parameters = json.load(f)
session = Session.builder.configs(connection_parameters).create()
print(f"Current Database and schema: {session.get_fully_qualified_current_schema()}")
print(f"Current Warehouse: {session.get_current_warehouse()}")

# Creating a Snowpark DataFrame
catalog_sales = session.table("CATALOG_SALES")
item = session.table("ITEM")


sales_data = (
    catalog_sales.join(item, on=F.col("CS_ITEM_SK") == F.col("I_ITEM_SK"), how="inner")[
        "I_CATEGORY", "I_COLOR", "CS_EXT_SALES_PRICE"
    ]
    .limit(100000)
    .to_pandas()
)

color_options = sales_data["I_COLOR"].unique().tolist()


app_ui = ui.page_fluid(
    ui.layout_sidebar(
        ui.panel_sidebar(ui.input_select("color", "Color", color_options)),
        ui.panel_main(output_widget("total_sales")),
    )
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.Calc
    def sub_sales_data():
        index_category = sales_data["I_COLOR"].isin([input.color()])
        sub_sales_data = sales_data[index_category]

        return sub_sales_data

    # total sales revenue plot
    @output
    @render_widget
    def total_sales():
        total_sales = px.bar(
            sub_sales_data()
            .groupby("I_CATEGORY")["CS_EXT_SALES_PRICE"]
            .sum()
            .reset_index()
            .sort_values(by="CS_EXT_SALES_PRICE", ascending=True),
            color="I_CATEGORY",
            x="I_CATEGORY",
            y="CS_EXT_SALES_PRICE",
            title="Total Sales Revenue by Category",
            labels={
                "I_CATEGORY": "Product Category",
                "CS_EXT_SALES_PRICE": "Total Sales Revenue($)",
            },
        )
        return total_sales


app = App(app_ui, server)
