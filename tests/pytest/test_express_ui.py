import pytest

from shiny import render, ui
from shiny.express import output_args, suspend_display


def test_render_output_controls():
    @render.text
    def text1():
        return "text"

    assert (
        ui.TagList(text1.tagify()).get_html_string()
        == ui.output_text_verbatim("text1").get_html_string()
    )

    @suspend_display
    @render.text
    def text2():
        return "text"

    assert ui.TagList(text2.tagify()).get_html_string() == ""

    @output_args(placeholder=True)
    @render.text
    def text3():
        return "text"

    assert (
        ui.TagList(text3.tagify()).get_html_string()
        == ui.output_text_verbatim("text3", placeholder=True).get_html_string()
    )

    @output_args(width=100)
    @render.text
    def text4():
        return "text"

    with pytest.raises(TypeError, match="width"):
        text4.tagify()
