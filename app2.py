from shiny import *
from htmltools import *

ui = page_fluid(
  navs_tab_card(
    nav(tags.b("a"), "tab a"),
    nav("b", "tab b"),
    nav_spacer(),
    nav_menu("menu", nav("c", "tab c"), align = "right")
  )
)

ui.show()


ui = page_navbar(
  nav("a", "tab a"),
  nav("b", "tab b"),
  nav_spacer(),
  nav_menu("menu", nav("c", "tab c"), align="right"),
  title = "navbar"
)

ui.show()