from htmltools import *
from shiny import *

ui = page_fluid(
  h1("Hello Shiny for Python!"),
  input_button("foo", "Hello!"),
  #input_slider("bar", "Hello slider", 0, 10, 1),
  navs_tab_card(
    nav("A", "tab a"),
    nav("B", "tab b")
  )
)

ui.show()
