import textwrap

from shiny import ui
from htmltools import HTMLDocument, TagList, tags


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

    title = TagList(
        tags.h1("A title"),
        tags.script("foo"),
        tags.style("foo"),
        tags.h5(tags.script("foo"), "A subtitle"),
    )

    x = HTMLDocument(ui.panel_title(title)).render()["html"]
    assert x == textwrap.dedent(
        """\
        <!DOCTYPE html>
        <html>
          <head>
            <meta charset="utf-8"/>
            <script type="application/html-dependencies">headcontent_9e055af8ef9fa0fb1ba72eeba8053498fbc0d075[0.0]</script>
            <title>A title A subtitle</title>
          </head>
          <body>
            <h1>A title</h1>
            <script>foo</script>
            <style>foo</style>
            <h5>
              <script>foo</script>
              A subtitle
            </h5>
          </body>
        </html>"""
    )
