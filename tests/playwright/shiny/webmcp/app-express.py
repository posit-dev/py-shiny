from shiny import webmcp
from shiny.express import app_opts, input, ui

app_opts(webmcp=True)
ui.input_numeric("n", "Quantity", 2)


@webmcp.tool(
    description="Double the current quantity",
    input_schema={"type": "object", "properties": {}},
    read_only=True,
)
def double():
    return {"doubled": input.n() * 2}
