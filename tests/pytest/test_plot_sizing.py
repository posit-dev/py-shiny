from shiny import render, ui

# from shiny.types import MISSING


def test_decorator_plot_sizing():
    """render.plot width/height are passed through to implicit output"""

    @render.plot(width=1280, height=960)
    def foo():
        ...

    rendered = str(foo.tagify())
    assert "1280px" in rendered
    assert "960px" in rendered
    assert rendered == str(ui.output_plot("foo", width=1280, height=960))


def test_decorator_plot_default():
    """render.plot default is the same as ui.output_plot default"""

    @render.plot()
    def foo():
        ...

    rendered = str(foo.tagify())
    assert rendered == str(ui.output_plot("foo"))


# def test_decorator_ui_kwargs():
#     """@ui_kwargs is respected"""

#     @ui_kwargs(width="640px", height="480px")
#     @render.plot()
#     def foo():
#         ...

#     rendered = str(foo.tagify())
#     assert rendered == str(ui.output_plot("foo", width="640px", height="480px"))


# def test_decorator_ui_kwargs_priority():
#     """@ui_kwargs should override render.plot width/height"""

#     @ui_kwargs(width="640px", height=480)
#     @render.plot(width=1280, height=960)
#     def foo():
#         ...

#     rendered = str(foo.tagify())
#     # Note "640px" => 640 and 480 => "480px"
#     assert rendered == str(ui.output_plot("foo", width=640, height="480px"))


# def test_decorator_ui_kwargs_MISSING():
#     """Not saying we support this, but test how MISSING interacts"""

#     @ui_kwargs(width=MISSING)
#     @render.plot(width=1280, height=MISSING)
#     def foo():
#         ...

#     rendered = str(foo.tagify())
#     assert rendered == str(ui.output_plot("foo", width="1280px"))
