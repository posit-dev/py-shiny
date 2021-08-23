from htmltools import *
from shiny.page import *
from shiny.input import *

ui = fluid(
  h1("Hello Shiny for Python!"),
  action_button("foo", "Hello!"),
  slider("bar", "Hello slider", 0, 10, 1)
)

ui.show()
