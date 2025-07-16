from htmltools import css

from shiny.ui import input_dark_mode


def test_input_dark_mode_style():
    base = input_dark_mode()
    base_style = base.attrs["style"]
    assert isinstance(base_style, str)

    dark_mode = input_dark_mode(style="color: red;")
    assert dark_mode.attrs["style"] == base_style + " color: red;"

    css_position = css(position="absolute", top="1em", left="1em")
    assert isinstance(css_position, str)

    dark_mode = input_dark_mode(style=css_position)
    assert dark_mode.attrs["style"] == base_style + " " + css_position
