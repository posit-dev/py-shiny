from shiny.express import expressify, ui


# @expressify converts a function to work with Express syntax
@expressify
def expressified1(s: str):
    f"Expressified function 1: {s}"
    ui.br()


expressified1("Hello")

expressified1("world")


ui.br()


# @expressify() also works with parens
@expressify()
def expressified2(s: str):
    f"Expressified function 2: {s}"
    ui.br()


expressified2("Hello")

expressified2("world")
