from htmltools import *

# keyword args must come after positional args!
html = div(
    span("Hello htmltools!"),
    id = "foo",
    # class is a keyword, so we support the JSX className
    className = "bar",
    # Any '_' is translated to '-'
    data_foo = "bar"
)
print(html)

# Similar to R, common tags (e.g., div(), span()) are 'exported' at the
# top-level of the module, but tags contains all the tags
tags.video().render()


dep = html_dependency(
    name = "foo",
    version = "1.0",
    package = "prism",
    src = "www"
)


from ui import input, output, page
ui = page.fluid(
    output.text("txt"),
    input.slider("n", "Choose n", 0, 100, 50),
    title = "Prism demo"
)
print(ui)





