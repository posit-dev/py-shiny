from shiny import webmcp
from shiny.express import input, ui

ui.input_numeric("n", "Quantity", 2)


@webmcp.tool(
    description="Double the current quantity",
    input_schema={"type": "object", "properties": {}},
    read_only=True,
)
def double():
    return {"doubled": input.n() * 2}
