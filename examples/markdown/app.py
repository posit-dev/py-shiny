from shiny import *

ui = page_fluid(
    markdown(
        """
# Hello World

This is **markdown** and here is some code:

```python
print('Hello world!')
```

And here is some [link](https://www.google.com).

What about some arbitrary HTML <a href="https://www.google.com">link</a>?
        """
    )
)


def server(session: ShinySession):
    pass


ShinyApp(ui, server).run()
