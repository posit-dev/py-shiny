import textwrap

from htmltools import HTMLDocument, TagList, tags

from shiny import ui
from shiny.ui._input_select import _update_options


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


def test_modal_footer():
    # Default behavior: Dismiss button
    x = str(ui.modal())
    assert x == textwrap.dedent(
        """\
        <div id="shiny-modal" class="modal fade" tabindex="-1" data-backdrop="static" data-bs-backdrop="static" data-keyboard="false" data-bs-keyboard="false">
          <div class="modal-dialog">
            <div class="modal-content">
              <div class="modal-body"></div>
              <div class="modal-footer">
                <button class="btn btn-default" type="button" data-dismiss="modal" data-bs-dismiss="modal">Dismiss</button>
              </div>
            </div>
          </div>
          <script>if (window.bootstrap && !window.bootstrap.Modal.VERSION.match(/^4\\. /)) {
          var modal=new bootstrap.Modal(document.getElementById('shiny-modal'))
          modal.show()
        } else {
          $('#shiny-modal').modal().focus()
        }</script>
        </div>"""
    )

    # None: drop footer altogether
    x = str(ui.modal(footer=None))
    assert x == textwrap.dedent(
        """\
        <div id="shiny-modal" class="modal fade" tabindex="-1" data-backdrop="static" data-bs-backdrop="static" data-keyboard="false" data-bs-keyboard="false">
          <div class="modal-dialog">
            <div class="modal-content">
              <div class="modal-body"></div>
            </div>
          </div>
          <script>if (window.bootstrap && !window.bootstrap.Modal.VERSION.match(/^4\\. /)) {
          var modal=new bootstrap.Modal(document.getElementById('shiny-modal'))
          modal.show()
        } else {
          $('#shiny-modal').modal().focus()
        }</script>
        </div>"""
    )

    # If other falsy value: Render empty footer
    x = str(ui.modal(footer=""))
    assert x == textwrap.dedent(
        """\
        <div id="shiny-modal" class="modal fade" tabindex="-1" data-backdrop="static" data-bs-backdrop="static" data-keyboard="false" data-bs-keyboard="false">
          <div class="modal-dialog">
            <div class="modal-content">
              <div class="modal-body"></div>
              <div class="modal-footer"></div>
            </div>
          </div>
          <script>if (window.bootstrap && !window.bootstrap.Modal.VERSION.match(/^4\\. /)) {
          var modal=new bootstrap.Modal(document.getElementById('shiny-modal'))
          modal.show()
        } else {
          $('#shiny-modal').modal().focus()
        }</script>
        </div>"""
    )

    # Anything else: include custom footer
    x = str(ui.modal(footer=ui.span("Custom Footer", class_="mt-3")))
    assert x == textwrap.dedent(
        """\
        <div id="shiny-modal" class="modal fade" tabindex="-1" data-backdrop="static" data-bs-backdrop="static" data-keyboard="false" data-bs-keyboard="false">
          <div class="modal-dialog">
            <div class="modal-content">
              <div class="modal-body"></div>
              <div class="modal-footer">
                <span class="mt-3">Custom Footer</span>
              </div>
            </div>
          </div>
          <script>if (window.bootstrap && !window.bootstrap.Modal.VERSION.match(/^4\\. /)) {
          var modal=new bootstrap.Modal(document.getElementById('shiny-modal'))
          modal.show()
        } else {
          $('#shiny-modal').modal().focus()
        }</script>
        </div>"""
    )


def test__update_options():
    # User does not supply options
    assert _update_options({}, remove_button=False, multiple=True) == {}
    assert _update_options({}, remove_button=True, multiple=True) == {
        "plugins": ["remove_button"]
    }
    assert _update_options({}, remove_button=True, multiple=False) == {
        "plugins": ["clear_button"]
    }

    # User supplies other plugins
    d1 = {"plugins": ["foo", "bar"]}
    assert _update_options(d1, remove_button=True, multiple=True) == {
        "plugins": ["foo", "bar", "remove_button"]
    }
    assert _update_options(d1, remove_button=True, multiple=False) == {
        "plugins": ["foo", "bar", "clear_button"]
    }
    assert _update_options(d1, remove_button=False, multiple=False) == {
        "plugins": ["foo", "bar"]
    }

    # User supplies non-plugin options
    d2 = {"other_key": "foo"}

    assert _update_options(d2, remove_button=True, multiple=True) == {
        "other_key": "foo",
        "plugins": ["remove_button"],
    }
    assert _update_options(d2, remove_button=True, multiple=True) == {
        "other_key": "foo",
        "plugins": ["remove_button"],
    }
    assert _update_options(d2, remove_button=False, multiple=False) == d2

    # User supplies clear button plugin
    d3 = {"plugins": ["clear_button"]}

    assert _update_options(d3, remove_button=True, multiple=True) == {
        "plugins": ["clear_button", "remove_button"]
    }

    assert _update_options(d3, remove_button=False, multiple=True) == d3
    assert _update_options(d3, remove_button=True, multiple=False) == d3

    # User supplies both clear and remove button plugins
    d4 = {"plugins": ["clear_button", "remove_button"]}

    assert _update_options(d4, remove_button=True, multiple=True) == d4
    assert _update_options(d4, remove_button=True, multiple=False) == d4
    assert _update_options(d4, remove_button=False, multiple=False) == d4
