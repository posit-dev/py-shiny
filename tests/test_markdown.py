from shiny.ui import markdown
from htmltools import HTML


def test_markdown():
    assert markdown("# a top level") == HTML("<h1>a top level</h1>\n")
    assert markdown("## a subheading") == HTML("<h2>a subheading</h2>\n")
    assert markdown("[rstudio](https://rstudio.com)") == HTML(
        '<p><a href="https://rstudio.com">rstudio</a></p>\n'
    )

    assert markdown("a ~~paragraph~~ with a link: https://example.com") == HTML(
        '<p>a <s>paragraph</s> with a link: <a href="https://example.com">https://example.com</a></p>\n'
    )

    assert (
        markdown(
            """
        # Hello World

        This is **markdown** and here is some `code`:

        ```python
        print('Hello world!')
        ```
        """
        )
        == HTML(
            "<h1>Hello World</h1>\n<p>This is <strong>markdown</strong> and here is some <code>code</code>:</p>\n<pre><code class=\"language-python\">print('Hello world!')\n</code></pre>\n"
        )
    )

    assert (
        markdown(
            """
        # Hello World

        This is **markdown** and here is some `code`:

            print('Hello world!')
        """
        )
        == HTML(
            "<h1>Hello World</h1>\n<p>This is <strong>markdown</strong> and here is some <code>code</code>:</p>\n<pre><code>print('Hello world!')\n</code></pre>\n"
        )
    )
