import textwrap

from shiny import ui
from htmltools import HTMLDocument


def test_panel_title():
    x = HTMLDocument(ui.panel_title("Hello Shiny UI")).render()["html"]
    assert x == textwrap.dedent(
        """\
        <!DOCTYPE html>
        <html>
          <head>
            <meta charset="utf-8"/>
            <script type="application/html-dependencies">headcontent_648f698a6bce952fe1b165140306e01f4da9e164[0.0]</script>
            <title>Hello Shiny UI</title>
          </head>
          <body>
            <h2>Hello Shiny UI</h2>
          </body>
        </html>"""
    )
