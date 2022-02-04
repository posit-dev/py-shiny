import textwrap

import commonmark
from htmltools import HTML


def markdown(x: str, smart: bool = True) -> HTML:
    parser = commonmark.Parser({smart: smart})
    # x = textwrap.dedent(x)
    ast = parser.parse(x)
    renderer = commonmark.HtmlRenderer()
    return HTML(renderer.render(ast))


# from htmltools import JSXTag, jsx_tag_create, HTMLDependency
# def markdown(x: str, options: Dict[str, object] = {}) -> JSXTag:
#    Markdown = jsx_tag_create("MarkdownToJSX", allowedProps=["options"])
#    return Markdown(textwrap.dedent(x), _markdown_deps(), options=options)
#
#
# def _markdown_deps() -> HTMLDependency:
#    return HTMLDependency(
#        "markdown-to-jsx",
#        version="7.1.6",
#        source={"package": "shiny", "subdir": "www/shared/markdown-to-jsx"},
#        script={"src": "index.min.js"},
#    )
#
